# [H] Gophish contains a denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-42jc-v69j-g38f
CVE: CVE-2026-39904
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-42jc-v69j-g38f
Type: github-advisory

## Affected
- Go: `github.com/gophish/gophish` — affected >=0

## Details
Gophish through 0.12.1 contains a denial of service vulnerability that allows authenticated users with the User role to exhaust server memory by uploading a crafted Office document as an email template attachment. The ApplyTemplate() function in models/attachment.go processes Office documents as ZIP archives and calls ioutil.ReadAll() on each contained file entry without enforcing size restrictions on uncompressed content, allowing a zip bomb payload to expand to several gigabytes in memory and cause the process to be terminated by the operating system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-39904
- https://github.com/ashikmd7/GoPhish-0.12.1/blob/main/Unbounded%20Memory%20Allocation%20in%20Office%20Attachment%20Processing%20Leads%20to%20Server%20DoS/README.md
- https://github.com/gophish/gophish
- https://www.vulncheck.com/advisories/gophish-denial-of-service-via-office-document-upload
