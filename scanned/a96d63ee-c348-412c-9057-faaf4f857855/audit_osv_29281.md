# [M] CVE-2024-41254

## Summary
Severity: Medium
Advisory: CVE-2024-41254
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2024-07-31
Source: https://osv.dev/vulnerability/CVE-2024-41254
Type: osv

## Details
An issue was discovered in litestream v0.3.13. The usage of the ssh.InsecureIgnoreHostKey() disables host key verification, possibly allowing attackers to obtain sensitive information via a man-in-the-middle attack.

## References
- https://gist.github.com/nyxfqq/d857f268a53aa62402655c8dcd95c68f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41254.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41254
