# [M] Open Redirection in pyload/pyload

## Summary
Severity: Medium
Advisory: CVE-2024-1240
Aliases: PYSEC-2024-123
CVSS: 4.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:L)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2024-1240
Type: osv

## Details
An open redirection vulnerability exists in pyload/pyload version 0.5.0. The vulnerability is due to improper handling of the 'next' parameter in the login functionality. An attacker can exploit this vulnerability to redirect users to malicious sites, which can be used for phishing or other malicious activities. The issue is fixed in pyload-ng 0.5.0b3.dev79.

## References
- https://huntr.com/bounties/eef9513d-ccc3-4030-b574-374c5e7b887e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1240.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1240
- https://github.com/pyload/pyload/commit/fe94451dcc2be90b3889e2fd9d07b483c8a6dccd
