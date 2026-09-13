# [C] ZAP ViewState Add-on Insecure Deserialization via JSFViewState.decode()

## Summary
Severity: Critical
Advisory: CVE-2026-57527
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-57527
Type: osv

## Details
Zed Attack Proxy (ZAP) ViewState add-on before version 4 contains an insecure deserialization vulnerability that allows attackers who control a proxied web server to achieve arbitrary code execution by embedding a malicious serialized Java object in the javax.faces.ViewState HTTP response parameter. The JSFViewState.decode() method base64-decodes the ViewState value and passes it directly to ObjectInputStream.readObject() without a deserialization filter, allowlist, or type restriction, causing the malicious object to be deserialized within the ZAP JVM when the Desktop UI renders the ViewState panel.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57527.json
- https://github.com/zaproxy/zap-extensions/releases/tag/viewstate-v4
- https://nvd.nist.gov/vuln/detail/CVE-2026-57527
- https://www.vulncheck.com/advisories/zap-viewstate-add-on-insecure-deserialization-via-jsfviewstate-decode
- https://www.zaproxy.org/blog/2026-06-24-java-deserialization-vulnerability-in-zap-viewstate-addon/
- https://github.com/zaproxy/zap-extensions/pull/7481
- https://github.com/zaproxy/zap-extensions/commit/ac6c3f94d38505bc0facea286a4d3728044c6e5c
- https://github.com/zaproxy/zap-extensions
