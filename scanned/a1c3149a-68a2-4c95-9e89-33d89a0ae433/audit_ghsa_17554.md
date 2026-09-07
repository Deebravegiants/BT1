# [M] @vue/cli-plugin-pwa Regular Expression Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-79vf-hf9f-j9q8
CVE: CVE-2025-5897
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-06-09
Source: https://github.com/advisories/GHSA-79vf-hf9f-j9q8
Type: github-advisory

## Affected
- npm: `@vue/cli-plugin-pwa` — affected >=0

## Details
A vulnerability was found in vuejs vue-cli up to 5.0.8. It has been rated as problematic. This issue affects the function HtmlPwaPlugin of the file packages/@vue/cli-plugin-pwa/lib/HtmlPwaPlugin.js of the component Markdown Code Handler. The manipulation leads to inefficient regular expression complexity. The attack may be initiated remotely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5897
- https://github.com/vuejs/vue-cli/pull/7478
- https://github.com/vuejs/vue-cli
- https://vuldb.com/?ctiid.311669
- https://vuldb.com/?id.311669
- https://vuldb.com/?submit.585798
