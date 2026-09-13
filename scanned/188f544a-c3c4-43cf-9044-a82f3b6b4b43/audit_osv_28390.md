# [C] Path Traversal in gaizhenbiao/chuanhuchatgpt

## Summary
Severity: Critical
Advisory: CVE-2024-3234
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-06
Source: https://osv.dev/vulnerability/CVE-2024-3234
Type: osv

## Details
The gaizhenbiao/chuanhuchatgpt application is vulnerable to a path traversal attack due to its use of an outdated gradio component. The application is designed to restrict user access to resources within the `web_assets` folder. However, the outdated version of gradio it employs is susceptible to path traversal, as identified in CVE-2023-51449. This vulnerability allows unauthorized users to bypass the intended restrictions and access sensitive files, such as `config.json`, which contains API keys. The issue affects the latest version of chuanhuchatgpt prior to the fixed version released on 20240305.

## References
- https://huntr.com/bounties/277e3ff0-5878-4809-a4b9-73cdbb70dc9f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3234.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3234
- https://github.com/gaizhenbiao/chuanhuchatgpt/commit/6b8f7db347b390f6f8bd07ea2a4ef01a47382f00
