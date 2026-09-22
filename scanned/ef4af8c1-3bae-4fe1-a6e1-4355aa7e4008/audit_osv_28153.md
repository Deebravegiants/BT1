# [H] CVE-2024-28286

## Summary
Severity: High
Advisory: CVE-2024-28286
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-20
Source: https://osv.dev/vulnerability/CVE-2024-28286
Type: osv

## Details
In mz-automation libiec61850 v1.4.0, a NULL Pointer Dereference was detected in the mmsServer_handleFileCloseRequest.c function of src/mms/iso_mms/server/mms_file_service.c. The vulnerability manifests as SEGV and causes the application to crash

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28286.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-28286
- https://github.com/mz-automation/libiec61850/issues/496
