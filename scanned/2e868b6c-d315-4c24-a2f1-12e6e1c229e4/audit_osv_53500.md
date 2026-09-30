# [H] CVE-2022-46289

## Summary
Severity: High
Advisory: CVE-2022-46289
Aliases: GHSA-rj4c-r689-cm87, PYSEC-2026-2790
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-07-21
Source: https://osv.dev/vulnerability/CVE-2022-46289
Type: osv

## Details
Multiple out-of-bounds write vulnerabilities exist in the ORCA format nAtoms functionality of Open Babel 3.1.1 and master commit 530dbfa3. A specially-crafted malformed file can lead to arbitrary code execution. An attacker can provide a malicious file to trigger this vulnerability.nAtoms calculation wrap-around, leading to a small buffer allocation

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2022-1665
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1665
