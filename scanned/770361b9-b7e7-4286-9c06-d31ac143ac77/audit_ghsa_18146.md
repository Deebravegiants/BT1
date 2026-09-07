# [M] Element Plus Link component (el-link) implements insufficient input validation for the href attribute

## Summary
Severity: Medium
Advisory: GHSA-5m5x-9j46-h678
CVE: CVE-2025-57665
CWE: CWE-116, CWE-20
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-5m5x-9j46-h678
Type: github-advisory

## Affected
- npm: `element-plus` — affected >=0

## Details
Element Plus Link component (el-link) prior to 2.11.0 implements insufficient input validation for the href attribute, creating a security abstraction gap that obscures URL-based attack vectors. The component passes user-controlled href values directly to underlying anchor elements without protocol validation, URL sanitization, or security headers. This allows attackers to inject malicious URLs using dangerous protocols (javascript:, data:, file:) or redirect users to external malicious sites. While native HTML anchor elements present similar risks, UI component libraries bear additional responsibility for implementing security safeguards and providing clear risk documentation. The vulnerability enables XSS attacks, phishing campaigns, and open redirect exploits affecting applications that use Element Plus Link components with user-controlled or untrusted URL inputs.  As of version 2.11.0, Element Plus have clearly documented the risks inherent with the component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57665
- https://github.com/element-plus/element-plus/pull/21711
- https://github.com/element-plus/element-plus/commit/110d4e1d7e150ccb829771c7319d31ce777d102f
- https://element-plus.org/en-US/component/link.html
- https://github.com/element-plus/element-plus
- https://github.com/element-plus/element-plus/blob/dev/packages/components/link/src/link.vue
- https://www.npmjs.com/package/element-plus
