# [H] CVE-2025-1862

## Summary
Severity: High
Advisory: CVE-2025-1862
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-26
Source: https://osv.dev/vulnerability/CVE-2025-1862
Type: osv

## Details
An arbitrary file upload vulnerability exists in multiple WSO2 products due to improper validation of user-supplied filenames in the BPEL uploader SOAP service endpoint. A malicious actor with administrative privileges can upload arbitrary files to a user-controlled location on the server.


By leveraging this vulnerability, an attacker can upload a specially crafted payload and achieve remote code execution (RCE), potentially compromising the server and its data.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2025/WSO2-2025-3992/
