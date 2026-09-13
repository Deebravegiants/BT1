# [M] Nuxt OG Image is vulnerable to Denial of Service via unbounded image dimensions

## Summary
Severity: Medium
Advisory: GHSA-c7xp-q6q8-hg76
CVE: CVE-2026-34404
CWE: CWE-400, CWE-404
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-c7xp-q6q8-hg76
Type: github-advisory

## Affected
- npm: `nuxt-og-image` — affected >=0 <6.2.5

## Details
**Product:** Nuxt OG Image 
**Version:** 6.1.2
**CWE-ID:** [CWE-404](https://cwe.mitre.org/data/definitions/404.html): Improper Resource Shutdown or Release
**Description:** Failure to limit the length and width of the generated image results in a denial of service.
**Impact:** Denial of service
**Exploitation condition:** An external user
**Mitigation:** Implement a limitation on the width and length of the generated image.
**Researcher:** Dmitry Prokhorov (Positive Technologies)

## Research 
During the analysis of the nuxt-og-image package, which is shipped with the nuxt-seo package, a zero‑day vulnerability was discovered.
This research revealed that the image‑generation component by the URI: `/_og/d/` (and, in older versions, `/og-image/`) contains a Denial of Service (DoS) vulnerability. The issue arises because there is no restriction on the width and height parameters of the generated image. The vulnerability was reproduced using the standard configuration and the default templates.

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
To demonstrate the proof‑of‑concept, a request should be sent with the increased `width` and `height` parameters. This will cause a delay and exhaust the server’s resources during image generation.

_Listing 2. HTTP-request example_
```
GET /_og/d/og.png?width=20000&height=20000 HTTP/1.1
Host: web-test.local:3000
```

_Figure 1. HTTP-response: denial-of-service error_
<img width="974" height="663" alt="image" src="https://github.com/user-attachments/assets/ff625249-2e0d-4a03-a734-3a77fd0cbb81" />

After sending a HTTP-request, the test server's memory was exhausted.

_Figure 2. Video memory exhausted error_
<img width="863" height="1033" alt="image" src="https://github.com/user-attachments/assets/66b5919a-f039-468e-812e-1f709c468287" />


## Credits
Researcher: Dmitry Prokhorov (Positive Technologies)

## References
- https://github.com/nuxt-modules/og-image/security/advisories/GHSA-c7xp-q6q8-hg76
- https://nvd.nist.gov/vuln/detail/CVE-2026-34404
- https://github.com/nuxt-modules/og-image
