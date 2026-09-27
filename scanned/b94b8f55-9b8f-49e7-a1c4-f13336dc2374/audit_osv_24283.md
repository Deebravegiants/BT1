# [M] mPDF 7.0 - Local File Inclusion

## Summary
Severity: Medium
Advisory: CVE-2022-50897
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2022-50897
Type: osv

## Details
mPDF 7.0 contains a local file inclusion vulnerability that allows attackers to read arbitrary system files by manipulating annotation file parameters. Attackers can generate URL-encoded or base64 payloads to include local files through crafted annotation content with file path specifications.

## References
- https://mpdf.github.io/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50897.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50897
- https://www.vulncheck.com/advisories/mpdf-local-file-inclusion
- https://www.exploit-db.com/exploits/50995
