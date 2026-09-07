# [H] Reflected cross-site scripting (XSS) vulnerability

## Summary
Severity: High
Advisory: GHSA-hrgx-7j6v-xj82
CVE: CVE-2022-0087
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2022-01-12
Source: https://github.com/advisories/GHSA-hrgx-7j6v-xj82
Type: github-advisory

## Affected
- npm: `@keystone-6/auth` — affected >=0 <1.0.2
- npm: `@keystone-next/auth` — affected >=0

## Details
This security advisory relates to a capability for an attacker to exploit a reflected cross-site scripting vulnerability when using the `@keystone-6/auth` package.

#### Impact
The vulnerability can impact users of the administration user interface when following an untrusted link to the `signin` or `init` page.
This is a targeted attack and may present itself in the form of phishing and or chained in conjunction with some other vulnerability.

## Vulnerability mitigation
Please upgrade to `@keystone-6/auth >= 1.0.2`, where this vulnerability has been closed.
If you are using `@keystone-next/auth`,  we **strongly** recommend you upgrade to `@keystone-6`.

### Workarounds
If for some reason you cannot upgrade the dependencies in software, you could alternatively

- disable the administration user interface, or 
- if using a reverse-proxy, strip query parameters when accessing the administration interface

### References
https://owasp.org/www-community/attacks/xss/

Thanks to Shivansh Khari (@Shivansh-Khari) for discovering and reporting this vulnerability

## References
- https://github.com/keystonejs/keystone/security/advisories/GHSA-hrgx-7j6v-xj82
- https://nvd.nist.gov/vuln/detail/CVE-2022-0087
- https://github.com/keystonejs/keystone/commit/96bf833a23b1a0a5d365cf394467a943cc481b38
- https://github.com/keystonejs/keystone
- https://huntr.dev/bounties/c9d7374f-2cb9-4bac-9c90-a965942f413e
