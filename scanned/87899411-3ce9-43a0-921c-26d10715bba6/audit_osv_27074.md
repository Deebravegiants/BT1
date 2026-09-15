# [H] Unauthenticated Denial of Service in shaunwei/realchar

## Summary
Severity: High
Advisory: CVE-2024-10051
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10051
Type: osv

## Details
Realchar version v0.0.4 is vulnerable to an unauthenticated denial of service (DoS) attack. The vulnerability exists in the file upload request handling, where appending characters, such as dashes (-), to the end of a multipart boundary in an HTTP request causes the server to continuously process each character. This leads to excessive resource consumption and renders the service unavailable. The issue is unauthenticated and does not require any user interaction, impacting all users of the service.

## References
- https://huntr.com/bounties/6db72368-e7bc-43ee-a4ae-6092f710c263
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10051.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10051
