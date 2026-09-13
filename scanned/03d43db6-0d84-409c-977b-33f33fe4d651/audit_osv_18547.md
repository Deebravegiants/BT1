# [H] CVE-2020-28600

## Summary
Severity: High
Advisory: CVE-2020-28600
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-05-10
Source: https://osv.dev/vulnerability/CVE-2020-28600
Type: osv

## Details
An out-of-bounds write vulnerability exists in the import_stl.cc:import_stl() functionality of Openscad openscad-2020.12-RC2. A specially crafted STL file can lead to code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1224
