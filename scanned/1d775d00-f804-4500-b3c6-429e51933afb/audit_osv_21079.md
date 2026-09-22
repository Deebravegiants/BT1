# [M] CVE-2021-40403

## Summary
Severity: Medium
Advisory: CVE-2021-40403
CVSS: 6.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2022-02-04
Source: https://osv.dev/vulnerability/CVE-2021-40403
Type: osv

## Details
An information disclosure vulnerability exists in the pick-and-place rotation parsing functionality of Gerbv 2.7.0 and dev (commit b5f1eacd), and Gerbv forked 2.8.0. A specially-crafted pick-and-place file can exploit the missing initialization of a structure to leak memory contents. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PTGBC37N2FV7NKOWFVCFMPAFYEPHSB7C/
- https://www.debian.org/security/2022/dsa-5306
- https://talosintelligence.com/vulnerability_reports/TALOS-2021-1417
