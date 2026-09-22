# [H] pydicom pynetdicom Library Path Traversal

## Summary
Severity: High
Advisory: CVE-2026-56445
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-56445
Type: osv

## Details
The qrscp application's C-STORE handler uses a specific instance from attacker-supplied DICOM datasets directly in os.path.join() without sanitization, allowing file writes to arbitrary paths.

## References
- https://github.com/cisagov/CSAF/blob/develop/csaf_files/OT/white/2026/icsma-26-176-01.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56445.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56445
- https://www.cisa.gov/news-events/ics-medical-advisories/icsma-26-176-01
- https://github.com/pydicom/pynetdicom
