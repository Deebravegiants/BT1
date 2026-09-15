# [H] NextChat Server-Side Request Forgery (SSRF)

## Summary
Severity: High
Advisory: CVE-2024-38514
Aliases: GHSA-gph5-rx77-3pjg
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-06-28
Source: https://osv.dev/vulnerability/CVE-2024-38514
Type: osv

## Details
NextChat is a cross-platform ChatGPT/Gemini UI. There is a Server-Side Request Forgery (SSRF) vulnerability due to a lack of validation of the `endpoint` GET parameter on the WebDav API endpoint. This SSRF can be used to perform arbitrary HTTPS request from the vulnerable instance (MKCOL, PUT and GET methods supported), or to target NextChat users and make them execute arbitrary JavaScript code in their browser. This vulnerability has been patched in version 2.12.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38514.json
- https://github.com/ChatGPTNextWeb/ChatGPT-Next-Web/security/advisories/GHSA-gph5-rx77-3pjg
- https://nvd.nist.gov/vuln/detail/CVE-2024-38514
- https://github.com/ChatGPTNextWeb/ChatGPT-Next-Web/commit/dad122199a85c2f12277593973e1784b212adf5e
