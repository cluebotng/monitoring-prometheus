#!/usr/bin/env python3
import os
from pathlib import PosixPath

import yaml


def generate_configuration() -> str:
    config = {
        "global": {
            "scrape_interval": "60s",
            "evaluation_interval": "60s",
            "scrape_timeout": "10s",
        },
        "scrape_configs": [],
        "alerting": {"alertmanagers": [{"static_configs": [{"targets": ["alertmanager:9093"]}]}]},
    }

    if rule_files := [
        path.absolute().as_posix() for path in (PosixPath(__file__).parent.parent / "rules").glob("*.yml")
    ]:
        config["rule_files"] = rule_files

    # Self
    config["scrape_configs"].append(
        {
            "job_name": "prometheus",
            "static_configs": [{"targets": ["localhost:9090"]}],
        }
    )

    # Alertmanager
    config["scrape_configs"].append(
        {
            "job_name": "alertmanager",
            "static_configs": [{"targets": ["alertmanager:9093"]}],
        }
    )

    # Checker
    config["scrape_configs"].append(
        {
            "job_name": "checker",
            "static_configs": [{"targets": ["checker:8090"]}],
        }
    )

    # Blackbox probes
    config["scrape_configs"].append(
        {
            "job_name": "blackbox",
            "metrics_path": "/probe",
            "params": {
                "module": [
                    "http_2xx",
                ],
            },
            "static_configs": [
                {
                    "targets": [
                        "cluebotng.toolforge.org",
                        "cluebotng-review.toolforge.org",
                        "cluebotng-editsets.toolforge.org",
                        "cluebotng-staging.toolforge.org",
                        "cluebotng-trainer.toolforge.org",
                    ]
                }
            ],
            "relabel_configs": [
                {
                    "source_labels": ["__address__"],
                    "target_label": "__param_target",
                },
                {"source_labels": ["__param_target"], "target_label": "instance"},
                {
                    "target_label": "__address__",
                    "replacement": "blackbox-exporter:9115",
                },
            ],
        }
    )

    # Blackbox metrics
    config["scrape_configs"].append(
        {
            "job_name": "blackbox_exporter",
            "static_configs": [{"targets": ["blackbox-exporter:9115"]}],
        }
    )

    # Note: Most metrics are pushed via grafana-alloy
    return yaml.dump(config)


def main():
    persistent_path = PosixPath(os.environ.get("TOOL_DATA_DIR")) / "persistent-data" / "prometheus"
    persistent_path.mkdir(parents=True, exist_ok=True)

    with open("/tmp/prometheus.yml", "w") as fh:
        fh.write(generate_configuration())

    return os.execv(
        "/workspace/bin/prometheus",
        [
            "/workspace/bin/prometheus",
            "--web.enable-remote-write-receiver",
            "--config.file",
            "/tmp/prometheus.yml",
            "--storage.tsdb.path",
            persistent_path.as_posix(),
            "--storage.tsdb.retention.time",
            "90d",
        ],
    )


if __name__ == "__main__":
    main()
