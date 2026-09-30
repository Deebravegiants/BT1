# [M] Cross-Site Request Forgery (CSRF) Leading to Account Takeover via SVG File Upload

## Summary
Severity: Medium
Advisory: CVE-2025-14202
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:H/VI:L/VA:N/SC:H/SI:N/SA:N)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-14202
Type: osv

## Details
A vulnerability in the file upload at bookmark + asset rendering pipeline allows an attacker to upload a malicious SVG file with JavaScript content. When an authenticated admin user views the SVG file with embedded JavaScript code of shared bookmark, JavaScript executes in the admin’s browser, retrieves the CSRF token, and sends a request to change the admin's password resulting in a full account takeover.

## References
- https://www.cve.org/cverecord?id=CVE-2025-14202
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14202.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-14202
- https://github.com/sissbruecker/linkding
