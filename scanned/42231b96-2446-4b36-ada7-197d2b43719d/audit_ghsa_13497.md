# [M] SpiceDB leaks information in log files when URI cannot be parsed

## Summary
Severity: Medium
Advisory: GHSA-jg7w-cxjv-98c2
CVE: CVE-2023-46255
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-31
Source: https://github.com/advisories/GHSA-jg7w-cxjv-98c2
Type: github-advisory

## Affected
- Go: `github.com/authzed/spicedb` — affected >=0 <1.27.0-rc1

## Details
SpiceDB is an open source, Google Zanzibar-inspired database for creating and managing security-critical application permissions. When the provided datastore URI is malformed (e.g. by having a password which contains `:`) the full URI (including the provided password) is printed, so that the password is shown in the logs. Version 1.27.0-rc1 patches this issue.

Example output:
```
terminated with errors error="unable to create migration driver for postgres: parse \"postgres://spicedb:<PASSWORD IN PLAINTEXT>": invalid port \"<PASSWORD IN PLAINTEXT>\" after host"
```

## References
- https://github.com/authzed/spicedb/security/advisories/GHSA-jg7w-cxjv-98c2
- https://nvd.nist.gov/vuln/detail/CVE-2023-46255
- https://github.com/authzed/spicedb/commit/ae50421b80f895e4c98d999b18e06b6f1e6f1cf8
- https://github.com/authzed/spicedb
