# [C] CVE-2025-50343

## Summary
Severity: Critical
Advisory: CVE-2025-50343
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2025-50343
Type: osv

## Details
An issue was discovered in matio 1.5.28. A heap-based memory corruption can occur in Mat_VarCreateStruct() when the nfields value does not match the actual number of strings in the fields array. This leads to out-of-bounds reads and invalid memory frees during cleanup, potentially causing a segmentation fault or heap corruption.

## References
- https://github.com/zakkanijia/POC/blob/main/matio/CVE-2025-50343/matio.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50343.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-50343
- https://github.com/tbeu/matio/issues/275
