# [H] Vitess users with backup storage access can gain unauthorized access to production deployment environments

## Summary
Severity: High
Advisory: GHSA-8g8j-r87h-p36x
CVE: CVE-2026-27965
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:H/VI:H/VA:L/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-8g8j-r87h-p36x
Type: github-advisory

## Affected
- Go: `vitess.io/vitess` — affected >=0

## Details
### Impact

Any user with read/write access to the backup storage location (e.g. an S3 bucket) can manipulate backup manifest files so that arbitrary code is later executed when that backup is restored. This can be used to provide that attacker with unintended/unauthorized access to the production deployment environment — allowing them to access information available in that environment as well as run any additional arbitrary commands there.

### Patches
Fixes are expected to be released with versions v23.0.3 and v22.0.4
See fix commit at https://github.com/vitessio/vitess/commit/4c0173293907af9cb942a6683c465c3f1e9fdb5c

### Workarounds

If maintainers *intended* to use an external decompressor then they can always specify that decompressor command in the `--external-decompressor` flag value for `vttablet` and `vtbackup`. That then overrides any value specified in the manifest file.

If maintainers did *not intend* to use an external decompressor, nor an internal one, then they can specify a value such as `cat` or `tee` in the `--external-decompressor` flag value for `vttablet` and `vtbackup` to ensure that a harmless command is always used. 

### References

Users can read more about the issue here: https://github.com/vitessio/vitess/issues/19459

## References
- https://github.com/vitessio/vitess/security/advisories/GHSA-8g8j-r87h-p36x
- https://nvd.nist.gov/vuln/detail/CVE-2026-27965
- https://github.com/vitessio/vitess/issues/19459
- https://github.com/vitessio/vitess/pull/19460
- https://github.com/vitessio/vitess/commit/4c0173293907af9cb942a6683c465c3f1e9fdb5c
- https://github.com/vitessio/vitess
