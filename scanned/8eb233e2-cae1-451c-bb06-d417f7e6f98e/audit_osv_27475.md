# [H] Improper Access Control in gaizhenbiao/chuanhuchatgpt

## Summary
Severity: High
Advisory: CVE-2024-2217
Aliases: PYSEC-2024-316
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2024-2217
Type: osv

## Details
gaizhenbiao/chuanhuchatgpt is vulnerable to improper access control, allowing unauthorized access to the `config.json` file. This vulnerability is present in both authenticated and unauthenticated versions of the application, enabling attackers to obtain sensitive information such as API keys (`openai_api_key`, `google_palm_api_key`, `xmchat_api_key`, etc.), configuration details, and user credentials. The issue stems from the application's handling of HTTP requests for the `config.json` file, which does not properly restrict access based on user authentication.

## References
- https://huntr.com/bounties/e4df74bf-b2ee-490f-a9c9-e5c8010b8b29
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2217.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2217
- https://github.com/gaizhenbiao/chuanhuchatgpt/commit/c5ae3b5ae6b47259e0ce8730e0a47e85121f4a7d
