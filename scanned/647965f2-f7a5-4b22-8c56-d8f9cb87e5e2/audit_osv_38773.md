# [M] linux-entra-sso: PRT SSO cookie can leak to attacker-controlled hosts when broad host permissions are granted

## Summary
Severity: Medium
Advisory: CVE-2026-42177
Aliases: GHSA-52rj-42vh-2rxc
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-42177
Type: osv

## Details
linux-entra-sso is a browser plugin for Linux to SSO on Microsoft Entra ID. Prior to 1.8.1, platform/chrome/js/platform-chrome.js:69-88 registers a single declarativeNetRequest rule whose urlFilter is Platform.SSO_URL + "/*", i.e. "https://login.microsoftonline.com/*". Chrome's urlFilter without a | or || anchor is substring-matched against the full request URL. The same applied rule action is modifyHeaders that attaches the Entra ID Primary Refresh Token cookie. The Firefox adapter in platform/firefox/js/platform-firefox.js:53 performs a belt-and-braces startsWith(Platform.SSO_URL) check before injecting the header; the Chrome adapter does not. When the extension holds broad host permissions through the optional_host_permissions: ["https://*/*"] declared in platform/chrome/manifest.json:34, a main-frame navigation to a URL whose path embeds https://login.microsoftonline.com/ causes Chrome to attach the PRT cookie to the request to the attacker-controlled host. This vulnerability is fixed in 1.8.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42177.json
- https://github.com/siemens/linux-entra-sso/security/advisories/GHSA-52rj-42vh-2rxc
- https://nvd.nist.gov/vuln/detail/CVE-2026-42177
