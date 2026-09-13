# [H] Denial of Service (DoS) by Sending Large Filename at File Upload Endpoint in gradio-app/gradio

## Summary
Severity: High
Advisory: CVE-2025-0187
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2025-0187
Type: osv

## Details
A Denial of Service (DoS) vulnerability was discovered in the file upload feature of gradio-app/gradio version 0.39.1. The vulnerability is due to improper handling of form-data with a large filename in the file upload request. By sending a payload with an excessively large filename, the server becomes overwhelmed and unresponsive, leading to unavailability for legitimate users.

## References
- https://huntr.com/bounties/77f3ed54-9e1c-4d9f-948f-ee6f82e2fe24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0187.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-0187
