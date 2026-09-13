# [M] CVE-2021-44962

## Summary
Severity: Medium
Advisory: CVE-2021-44962
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-03-01
Source: https://osv.dev/vulnerability/CVE-2021-44962
Type: osv

## Details
An out-of-bounds read vulnerability exists in the GCode::extrude() functionality of Slic3r libslic3r 1.3.0 and Master Commit b1a5500. A specially crafted stl file could lead to information disclosure. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://slic3r.org
- https://hackmd.io/KSI1bwGfSyO7T8UCf0HeTw
