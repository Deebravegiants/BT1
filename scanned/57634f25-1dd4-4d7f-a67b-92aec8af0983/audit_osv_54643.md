# [C] CVE-2024-23606

## Summary
Severity: Critical
Advisory: CVE-2024-23606
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-20
Source: https://osv.dev/vulnerability/CVE-2024-23606
Type: osv

## Details
An out-of-bounds write vulnerability exists in the sopen_FAMOS_read functionality of The Biosig Project libbiosig 2.5.0 and Master Branch (ab0ee111). A specially crafted .famos file can lead to arbitrary code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-1925
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OIRLGNQM33KAWVWP5RPMAPHWNP3IY5YW/
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-1925
