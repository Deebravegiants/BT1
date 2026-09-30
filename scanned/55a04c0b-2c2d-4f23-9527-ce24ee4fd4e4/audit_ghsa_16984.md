# [H] In Astro-Shield, setting a correct `integrity` attribute to injected code allows to bypass the allow-lists

## Summary
Severity: High
Advisory: GHSA-c4gr-q97g-ppwc
CVE: CVE-2024-30250
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-04-01
Source: https://github.com/advisories/GHSA-c4gr-q97g-ppwc
Type: github-advisory

## Affected
- npm: `@kindspells/astro-shield` — affected >=1.2.0 <1.3.2

## Details
### Impact

Versions from 1.2.0 to 1.3.1 of Astro-Shield allow to bypass the allow-lists for cross-origin resources by introducing valid `integrity` attributes to the injected code. This implies that the injected SRI hash would be added to the generated CSP header, which would lead the browser to believe that the injected resource is legit.

To exploit this vulnerability, the attacker needs to first inject code into the rendered pages by exploiting other not-related potential vulnerabilities.

### Patches

Version [1.3.2](https://github.com/kindspells/astro-shield/releases/tag/1.3.2) provides a patch.

### Workarounds
- To not use the middleware functionality of Astro-Shield.
- To use the middleware functionality of Astro-Shield ONLY for content that cannot be controlled in any way by external users.

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/kindspells/astro-shield/security/advisories/GHSA-c4gr-q97g-ppwc
- https://nvd.nist.gov/vuln/detail/CVE-2024-30250
- https://github.com/kindspells/astro-shield/commit/1221019306f501bf5fa9bcfb5a23a2321d34ba0a
- https://github.com/kindspells/astro-shield/commit/5ae8b8ef4f681d3a81431ee7e79d5dec545c6e1f
- https://github.com/kindspells/astro-shield
- https://github.com/kindspells/astro-shield/releases/tag/1.3.2
