# [M] CVE-2026-37504

## Summary
Severity: Medium
Advisory: CVE-2026-37504
CVSS: 5.3 (CVSS:3.1/AC:H/AV:N/A:N/C:H/I:N/PR:N/S:U/UI:R)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-37504
Type: osv

## Details
Sensitive server_token exposed via GET parameter in V2Board thru 1.7.4. In app/Http/Controllers/Server/UniProxyController.php, the server authentication token is accepted via GET parameter transmission. The token appears in URLs such as /api/v1/server/UniProxy/user?token=SECRET, causing it to be recorded in web server access logs, browser history, HTTP Referer headers, and proxy/CDN logs. An attacker who gains access to any log source can extract the token and impersonate a proxy server node, potentially intercepting all user traffic.

## References
- https://gist.github.com/sgInnora/1330e1a82caa79906eec55eeff2c99b9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37504.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-37504
- https://github.com/v2board/v2board
