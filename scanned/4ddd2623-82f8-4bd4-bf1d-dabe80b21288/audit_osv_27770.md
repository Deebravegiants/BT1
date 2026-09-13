# [H] IDOR make user can read e-mail log sent by other events

## Summary
Severity: High
Advisory: CVE-2024-25634
Aliases: GHSA-5wcv-pjc6-mxvv
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-19
Source: https://osv.dev/vulnerability/CVE-2024-25634
Type: osv

## Details
alf.io is an open source ticket reservation system. Prior to version 2.0-Mr-2402, an attacker can access data from other organizers. The attacker can use a specially crafted request to receive the e-mail log sent by other events. Version 2.0-M4-2402 fixes this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25634.json
- https://github.com/alfio-event/alf.io/security/advisories/GHSA-5wcv-pjc6-mxvv
- https://nvd.nist.gov/vuln/detail/CVE-2024-25634
