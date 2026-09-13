# [M] kedro-datasets has a path traversal vulnerability in PartitionedDataset that allows arbitrary file write

## Summary
Severity: Medium
Advisory: GHSA-cjg8-h5qc-hrjv
CVE: CVE-2026-35492
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-cjg8-h5qc-hrjv
Type: github-advisory

## Affected
- PyPI: `kedro-datasets` — affected >=0 <9.3.0

## Details
### Impact

PartitionedDataset in kedro-datasets was vulnerable to path traversal. Partition IDs were concatenated directly with the dataset base path without validation. An attacker or malicious input containing .. components in a partition ID could cause files to be written outside the configured dataset directory, potentially overwriting arbitrary files on the filesystem.
Users of PartitionedDataset with any storage backend (local filesystem, S3, GCS, etc.) are affected.

### Patches
Yes. The vulnerability has been patched in kedro-datasets version 9.3.0.
Users should upgrade to kedro-datasets >= 9.3.0. The fix normalizes constructed paths using `posixpath.normpath` and validates that the resolved path remains within the dataset base directory before use, raising a `DatasetError` if the path escapes the base directory.

### Workarounds
Users who cannot upgrade should validate partition IDs before passing them to PartitionedDataset, ensuring they do not contain `..` path components.

### References
Fix: https://github.com/kedro-org/kedro-plugins/pull/1346
Report: https://github.com/kedro-org/kedro/issues/5452

## References
- https://github.com/kedro-org/kedro-plugins/security/advisories/GHSA-cjg8-h5qc-hrjv
- https://nvd.nist.gov/vuln/detail/CVE-2026-35492
- https://github.com/kedro-org/kedro/issues/5452
- https://github.com/kedro-org/kedro-plugins/pull/1346
- https://github.com/kedro-org/kedro-plugins/commit/65115f76b872217317734b6bde8927170c98fc4b
- https://github.com/kedro-org/kedro-plugins
- https://github.com/kedro-org/kedro-plugins/releases/tag/kedro-datasets-9.3.0
