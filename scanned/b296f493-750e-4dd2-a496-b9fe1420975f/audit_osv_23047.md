# [M] CVE-2022-42705

## Summary
Severity: Medium
Advisory: CVE-2022-42705
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-05
Source: https://osv.dev/vulnerability/CVE-2022-42705
Type: osv

## Details
A use-after-free in res_pjsip_pubsub.c in Sangoma Asterisk 16.28, 18.14, 19.6, and certified/18.9-cert2 may allow a remote authenticated attacker to crash Asterisk (denial of service) by performing activity on a subscription via a reliable transport at the same time that Asterisk is also performing activity on that subscription.

## References
- https://downloads.asterisk.org/pub/security/AST-2022-008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/42xxx/CVE-2022-42705.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-42705
- https://www.debian.org/security/2023/dsa-5358
- https://lists.debian.org/debian-lts-announce/2023/02/msg00029.html
