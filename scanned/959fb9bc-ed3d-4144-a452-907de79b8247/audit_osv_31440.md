# [M] Grassroots DICOM (GDCM) Out-of-bounds Write

## Summary
Severity: Medium
Advisory: CVE-2025-11266
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-12
Source: https://osv.dev/vulnerability/CVE-2025-11266
Type: osv

## Details
An out-of-bounds write vulnerability exists in the Grassroots DICOM library (GDCM). The issue is triggered during parsing of a malformed DICOM file containing encapsulated PixelData fragments (compressed image data stored as multiple fragments). This vulnerability leads to a segmentation fault caused by an out-of-bounds memory access due to unsigned integer underflow in buffer indexing. It is exploitable via file input, simply opening a crafted malicious DICOM file is sufficient to trigger the crash, resulting in a denial-of-service condition.

## References
- https://github.com/cisagov/CSAF/blob/develop/csaf_files/OT/white/2025/icsma-25-345-01.json
- https://github.com/malaterre/GDCM/releases/tag/v3.2.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/11xxx/CVE-2025-11266.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-11266
- https://www.cisa.gov/news-events/ics-medical-advisories/icsma-25-345-01
- https://github.com/malaterre/GDCM/commit/5829c95c8ac3afa9a3a3413675e948959c28a789
