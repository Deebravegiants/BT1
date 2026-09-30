# [C] CVE-2021-40393

## Summary
Severity: Critical
Advisory: CVE-2021-40393
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-22
Source: https://osv.dev/vulnerability/CVE-2021-40393
Type: osv

## Details
An out-of-bounds write vulnerability exists in the RS-274X aperture macro variables handling functionality of Gerbv 2.7.0 and dev (commit b5f1eacd) and the forked version of Gerbv (commit 71493260). A specially-crafted gerber file can lead to code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2023/09/msg00040.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/37OSNNO5N5FJZP6ZBYRJMML5HYMJQIX7/
- https://www.debian.org/security/2022/dsa-5306
- https://talosintelligence.com/vulnerability_reports/TALOS-2021-1404
