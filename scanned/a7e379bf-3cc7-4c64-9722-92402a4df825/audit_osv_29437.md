# [H] CVE-2024-42415

## Summary
Severity: High
Advisory: CVE-2024-42415
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-03
Source: https://osv.dev/vulnerability/CVE-2024-42415
Type: osv

## Details
An integer overflow vulnerability exists in the Compound Document Binary File format parser of v1.14.52 of the GNOME Project G Structured File Library (libgsf). A specially crafted file can result in an integer overflow that allows for a heap-based buffer overflow when processing the sector allocation table. This can lead to arbitrary code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- http://www.openwall.com/lists/oss-security/2024/10/04/3
- https://lists.debian.org/debian-lts-announce/2024/10/msg00002.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-2069
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-2069
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42415.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42415
- https://gitlab.gnome.org/GNOME/libgsf/-/issues/34
