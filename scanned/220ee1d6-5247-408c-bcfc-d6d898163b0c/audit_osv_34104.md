# [C] OpenJPEG allows OOB heap memory write in opj_jp2_read_header

## Summary
Severity: Critical
Advisory: CVE-2025-54874
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-08-05
Source: https://osv.dev/vulnerability/CVE-2025-54874
Type: osv

## Details
OpenJPEG is an open-source JPEG 2000 codec. In OpenJPEG from 2.5.1 through 2.5.3, a call to opj_jp2_read_header may lead to OOB heap memory write when the data stream p_stream is too short and p_image is not initialized.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54874.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-54874
- https://securitylab.github.com/advisories/GHSL-2025-057_OpenCV
- https://github.com/uclouvain/openjpeg/commit/f809b80c67717c152a5ad30bf06774f00da4fd2d
- https://github.com/uclouvain/openjpeg/pull/1573
