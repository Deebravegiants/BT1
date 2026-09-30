# [H] CVE-2024-52333

## Summary
Severity: High
Advisory: CVE-2024-52333
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-13
Source: https://osv.dev/vulnerability/CVE-2024-52333
Type: osv

## Details
An improper array index validation vulnerability exists in the determineMinMax functionality of OFFIS DCMTK 3.6.8. A specially crafted DICOM file can lead to an out-of-bounds write. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://git.dcmtk.org/?p=dcmtk.git;a=commit;h=03e851b0586d05057c3268988e180ffb426b2e03
- https://lists.debian.org/debian-lts-announce/2025/01/msg00032.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-2121
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-2121
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52333.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52333
