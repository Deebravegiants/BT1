# [H] CVE-2021-21897

## Summary
Severity: High
Advisory: CVE-2021-21897
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-09-08
Source: https://osv.dev/vulnerability/CVE-2021-21897
Type: osv

## Details
A code execution vulnerability exists in the DL_Dxf::handleLWPolylineData functionality of Ribbonsoft dxflib 3.17.0. A specially-crafted .dxf file can lead to a heap buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5BUOTYU3KKIYE4BEBUFA4MRS462P3OWM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DA4C4X5GMM65VYLUW7Q7YL6P5NDB633A/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IMGMEPTYL7WTQ333J6SMC6MUHDMMWT3O/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/L2H36XRMAPQBIOVIIFX6KUT5YOG2ETM6/
- https://lists.debian.org/debian-lts-announce/2022/06/msg00008.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2021-1346
