# [H] CVE-2024-47796

## Summary
Severity: High
Advisory: CVE-2024-47796
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-13
Source: https://osv.dev/vulnerability/CVE-2024-47796
Type: osv

## Details
An improper array index validation vulnerability exists in the nowindow functionality of OFFIS DCMTK 3.6.8. A specially crafted DICOM file can lead to an out-of-bounds write. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://git.dcmtk.org/?p=dcmtk.git;a=commit;h=89a6e399f1e17d08a8bc8cdaa05b2ac9a50cd4f6
- https://lists.debian.org/debian-lts-announce/2025/01/msg00032.html
- https://lists.debian.org/debian-lts-announce/2025/06/msg00025.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-2122
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-2122
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47796.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47796
