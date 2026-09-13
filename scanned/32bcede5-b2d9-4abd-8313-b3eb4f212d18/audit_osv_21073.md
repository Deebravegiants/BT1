# [C] CVE-2021-40391

## Summary
Severity: Critical
Advisory: CVE-2021-40391
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-19
Source: https://osv.dev/vulnerability/CVE-2021-40391
Type: osv

## Details
An out-of-bounds write vulnerability exists in the drill format T-code tool number functionality of Gerbv 2.7.0, dev (commit b5f1eacd), and the forked version of Gerbv (commit 71493260). A specially-crafted drill file can lead to code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TUM5GIUZJ7AVHVCXDZW6ZVCAPV2ISN47/
- https://lists.debian.org/debian-lts-announce/2021/12/msg00003.html
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2021-1402
