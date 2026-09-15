# [H] CVE-2025-57248

## Summary
Severity: High
Advisory: CVE-2025-57248
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2025-57248
Type: osv

## Details
A null pointer dereference vulnerability was discovered in SumatraPDF 3.5.2 during the processing of a crafted .djvu file. When the file is opened, the application crashes inside libmupdf.dll, specifically in the DataPool::has_data() function.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57248.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57248
- https://github.com/sumatrapdfreader/sumatrapdf/issues/5035
