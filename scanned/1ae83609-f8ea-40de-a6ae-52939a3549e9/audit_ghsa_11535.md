# [M] Nuxt OG Image is vulnerable to reflected XSS via query parameter injection into HTML attributes

## Summary
Severity: Medium
Advisory: GHSA-mg36-wvcr-m75h
CVE: CVE-2026-34405
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-mg36-wvcr-m75h
Type: github-advisory

## Affected
- npm: `nuxt-og-image` — affected >=0 <6.2.5

## Details
**Product:** Nuxt OG Image 
**Version:** 6.1.2
**CWE-ID:** [CWE-79](https://cwe.mitre.org/data/definitions/79.html): Improper Neutralization of Input During Web Page Generation
**Description:** Incorrect parsing of GET parameters leads to the possibility of HTML injection and JavaScript code injection.
**Impact:** Client-Side JavaScript Execution
**Exploitation condition:** An external user
**Mitigation:** Correct the logic of parsing GET parameters and their subsequent implementation into the generated page.
**Researcher:** Dmitry Prokhorov (Positive Technologies)

## Research 
During the analysis of the nuxt-og-image package, which is shipped with the nuxt-seo package, a zero‑day vulnerability was discovered.
This research revealed that the image‑generation component by the URI: `/_og/d/` (and, in older versions, `/og-image/`) contains a vulnerability that allows injection of arbitrary attributes into the HTML page body. The vulnerability was reproduced using the standard configuration and the default templates.


_Listing 1. The content of the configuration file `nuxt.config.ts`_ 
```
export default defineNuxtConfig({
  modules: ['nuxt-og-image'],
  devServer: {
    host: 'web-test.local',
    port: 3000
  },
  site: {
    url: 'http://web-test.local:3000',
  },
  ogImage: {
    fonts: [
      'Inter:400', 
      'Inter:700'
    ],
  }
})
```

## Vulnerability reproduction
To demonstrate the proof‑of‑concept, follow the URI: `/_og/d/og.html?width=1000&height=1000&onmouseover=alert(document.cookie)&autofocus`
The injected parameters `onmouseover=alert(document.cookie)` and `autofocus` are treated as attributes and are inserted directly into the generated HTML page.


_Listing 2. HTTP-request example_
```
GET /_og/d/og.html?width=1000&height=1000&onmouseover=alert(document.cookie) HTTP/1.1
Host: web-test.local:3000
```

_Figure 1. The injected attribute in the HTML body_
<img width="974" height="670" alt="image" src="https://github.com/user-attachments/assets/d442c235-71a5-4da9-a963-8cf4b8614745" />

_Figure 2. JavaScript code execution_
<img width="974" height="291" alt="image" src="https://github.com/user-attachments/assets/01579f19-8e80-4fae-8516-5903370ee6d8" />


## Credits
Researcher: Dmitry Prokhorov (Positive Technologies)

## References
- https://github.com/nuxt-modules/og-image/security/advisories/GHSA-mg36-wvcr-m75h
- https://nvd.nist.gov/vuln/detail/CVE-2026-34405
- https://github.com/nuxt-modules/og-image
