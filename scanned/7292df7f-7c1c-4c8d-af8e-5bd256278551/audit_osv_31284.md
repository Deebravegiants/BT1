# [M] Misuse of SHA256 to create an encryption key

## Summary
Severity: Medium
Advisory: CVE-2024-7701
CVSS: 6.0 (CVSS:4.0/AV:P/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2024-12-15
Source: https://osv.dev/vulnerability/CVE-2024-7701
Type: osv

## Details
Use of Password Hash With Insufficient Computational Effort vulnerability in percona percona-toolkit allows Encryption Brute Forcing.This issue affects percona-toolkit: 3.6.0.

## References
- https://github.com/percona/percona-toolkit/blob/aa1ac0e6889168fddf73c3a72d447e9ea0c0c63b/src/go/pt-secure-collect/encrypt.go#L17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7701.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7701
- https://github.com/percona/percona-toolkit
