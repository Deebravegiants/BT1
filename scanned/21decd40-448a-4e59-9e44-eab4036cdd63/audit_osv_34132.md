# [M] CVE-2025-55127

## Summary
Severity: Medium
Advisory: CVE-2025-55127
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-11-20
Source: https://osv.dev/vulnerability/CVE-2025-55127
Type: osv

## Details
HackerOne community member Dao Hoang Anh (yoyomiski) has reported an improper neutralization of whitespace in the username when adding new users. A username with leading or trailing whitespace could be virtually indistinguishable from its legitimate counterpart when the username is displayed in the UI, potentially leading to confusion.

## References
- https://hackerone.com/reports/3413764
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55127.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-55127
