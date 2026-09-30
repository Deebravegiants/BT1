# [H] CVE-2020-28594

## Summary
Severity: High
Advisory: CVE-2020-28594
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-17
Source: https://osv.dev/vulnerability/CVE-2020-28594
Type: osv

## Details
A use-after-free vulnerability exists in the _3MF_Importer::_handle_end_model() functionality of Prusa Research PrusaSlicer 2.2.0 and Master (commit 4b040b856). A specially crafted 3MF file can lead to code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1218
