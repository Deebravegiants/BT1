# [M] CVE-2020-28590

## Summary
Severity: Medium
Advisory: CVE-2020-28590
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-04-13
Source: https://osv.dev/vulnerability/CVE-2020-28590
Type: osv

## Details
An out-of-bounds read vulnerability exists in the Obj File TriangleMesh::TriangleMesh() functionality of Slic3r libslic3r 1.3.0 and Master Commit 92abbc42. A specially crafted obj file could lead to information disclosure. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1213
