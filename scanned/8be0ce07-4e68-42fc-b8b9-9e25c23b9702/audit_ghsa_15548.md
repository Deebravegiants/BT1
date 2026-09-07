# [M] DOM clobbering could escalate to Cross-site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-gprj-6m2f-j9hx
CVE: CVE-2024-45389
CWE: CWE-79
Ecosystem: crates.io, npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2024-09-03
Source: https://github.com/advisories/GHSA-gprj-6m2f-j9hx
Type: github-advisory

## Affected
- npm: `pagefind` — affected >=0 <1.1.1
- npm: `@pagefind/default-ui` — affected >=0 <1.1.1
- npm: `@pagefind/modular-ui` — affected >=0 <1.1.1
- crates.io: `pagefind` — affected >=0 <1.1.1

## Details
Pagefind initializes its dynamic JavaScript and WebAssembly files relative to the location of the first script you load. This information is gathered by looking up the value of `document.currentScript.src`.

It is possible to "clobber" this lookup with otherwise benign HTML on the page, for example:
```html
<img name="currentScript" src="blob:https://xxx.xxx.xxx/ui.js"></img>
```

This will cause `document.currentScript.src` to resolve as an external domain, which will then be used by Pagefind to load dependencies.

This exploit would only work in the case that an attacker could inject HTML to your live, hosted, website. In these cases, this would act as a way to escalate the privilege available to an attacker. This assumes they have the ability to add some elements to the page (for example, `img` tags with a `name` attribute), but not others, as adding a `script` to the page would itself be the XSS vector.

Pagefind has tightened this resolution by ensuring the source is loaded from a valid script element. There are no reports of this being exploited in the wild via Pagefind.

### Original Report

If an attacker can inject benign html, such as:
`<img name="currentScript" src="blob:https://xxx.xxx.xxx/ui.js"></img>`

they can clobber `document.currentScript.src` leading to XSS in your library.

Here is the same attack on webpack that was accepted: https://github.com/webpack/webpack/security/advisories/GHSA-4vvj-4cpr-p986

## References
- https://github.com/CloudCannon/pagefind/security/advisories/GHSA-gprj-6m2f-j9hx
- https://github.com/webpack/webpack/security/advisories/GHSA-4vvj-4cpr-p986
- https://nvd.nist.gov/vuln/detail/CVE-2024-45389
- https://github.com/CloudCannon/pagefind/commit/14ec96864eabaf1d7d809d5da0186a8856261eeb
- https://github.com/CloudCannon/pagefind
