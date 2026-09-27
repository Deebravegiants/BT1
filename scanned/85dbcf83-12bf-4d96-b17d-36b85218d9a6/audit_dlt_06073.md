# [?] Fix panic when using packed config (#488)

## Summary
Severity: Unknown
Chain: Provenance
Component: provenance-io/provenance
Published: 2021-09-16
Source: https://github.com/provenance-io/provenance/commit/d8b5b38f93b1f5f05992f62e0c3e681b9c434434
Type: security-commit

## Details
Fix panic when using packed config (#488)

* [487]: Add a couple unit tests demonstrating the bug.

* [487]: Add changlog entry.

* [487]: Fix bug on providing the telemetry.global-labels to viper from a packed config.

* [487]: In the new unit tests, also assert that the returned config is equal to what was used to write the packed config.
