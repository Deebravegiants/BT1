# [M] CVE-2020-28591

## Summary
Severity: Medium
Advisory: CVE-2020-28591
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-03-03
Source: https://osv.dev/vulnerability/CVE-2020-28591
Type: osv

## Details
An out-of-bounds read vulnerability exists in the AMF File AMFParserContext::endElement() functionality of Slic3r libslic3r 1.3.0 and Master Commit 92abbc42. A specially crafted AMF file can lead to information disclosure. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TCSYYURJTUKJSEZIPDAXK4NHRXZMHIVA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WJPM24DY36EH3HFJGAXDLGFT43VZWLJ7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KBEK4H23AS6TKTGU2OTMHAZZYNECQVCB/
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1215
