# [M] Miniflux has an Open Redirect via protocol-relative redirect_url

## Summary
Severity: Medium
Advisory: GHSA-wqv2-4wpg-8hc9
CVE: CVE-2025-67713
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-wqv2-4wpg-8hc9
Type: github-advisory

## Affected
- Go: `miniflux.app/v2` — affected >=0 <2.2.15

## Details
### Summary
`redirect_url` is treated as safe when `url.Parse(...).IsAbs()` is false. Protocol-relative URLs like `//ikotaslabs.com` have an empty scheme and pass that check, allowing post-login redirects to attacker-controlled sites.

### Details
- `url.Parse("//ikotaslabs.com")` => empty Scheme, Host="ikotaslabs.com".
- `IsAbs()` returns false for `//ikotaslabs.com`, so the code treats it as allowed.
- Browser resolves `//ikotaslabs.com` to current-origin scheme (e.g. `https://ikotaslabs.com`), enabling phishing flows after login.

### PoC
1. Send or visit: `http://localhost/login?redirect_url=//ikotaslabs.com`  
2. Complete normal login flow.  
3. After login the app redirects to `https://ikotaslabs.com` (or `http://` depending on origin).

### Acknowledgements  
This vulnerability was discovered using the automated vulnerability analysis tools **VulScribe** and **PwnML**.   The research and tool development were conducted  with support from the **MITOU Advanced Program (未踏アドバンスト事業)**, implemented by the **Information-technology Promotion Agency (IPA), Japan**.

## References
- https://github.com/miniflux/v2/security/advisories/GHSA-wqv2-4wpg-8hc9
- https://nvd.nist.gov/vuln/detail/CVE-2025-67713
- https://github.com/miniflux/v2/commit/76df99f3a3db234cf6b312be5e771485213d03c7
- https://github.com/miniflux/v2
