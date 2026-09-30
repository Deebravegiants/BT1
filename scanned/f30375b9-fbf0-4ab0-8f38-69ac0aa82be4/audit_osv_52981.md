# [H] CVE-2022-23946

## Summary
Severity: High
Advisory: CVE-2022-23946
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-02-04
Source: https://osv.dev/vulnerability/CVE-2022-23946
Type: osv

## Details
A stack-based buffer overflow vulnerability exists in the Gerber Viewer gerber and excellon GCodeNumber parsing functionality of KiCad EDA 6.0.1 and master commit de006fc010. A specially-crafted gerber or excellon file can lead to code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5EMCGSSP3FIWCSL2KXVXLF35JYZKZE5Q/
- https://lists.debian.org/debian-lts-announce/2022/05/msg00009.html
- https://lists.debian.org/debian-lts-announce/2022/08/msg00010.html
- https://www.debian.org/security/2022/dsa-5214
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1460
