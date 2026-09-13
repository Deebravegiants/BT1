# [H] CVE-2022-46292

## Summary
Severity: High
Advisory: CVE-2022-46292
Aliases: GHSA-55f6-pf8r-c2f4, PYSEC-2026-2771
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-07-21
Source: https://osv.dev/vulnerability/CVE-2022-46292
Type: osv

## Details
Multiple out-of-bounds write vulnerabilities exist in the translationVectors parsing functionality in multiple supported formats of Open Babel 3.1.1 and master commit 530dbfa3. A specially-crafted malformed file can lead to arbitrary code execution. An attacker can provide a malicious file to trigger this vulnerability.This vulnerability affects the MOPAC file format, inside the Unit Cell Translation section

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2022-1666
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1666
