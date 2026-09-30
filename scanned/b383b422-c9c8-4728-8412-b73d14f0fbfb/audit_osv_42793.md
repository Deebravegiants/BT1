# [H] Nuxt: Server-Side Remote Code Execution via Runtime Template Injection in Nuxt Server Island Props

## Summary
Severity: High
Advisory: CVE-2026-71320
Aliases: GHSA-9473-5f9j-94wq
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71320
Type: osv

## Details
Nuxt is an open-source web development framework for Vue.js. From 3.4.0 until 3.21.10 and 4.5.1, an attacker can inject a template key through /__nuxt_island/ props into a dynamic component when `vue.runtimeCompiler: true` is enabled, causing template execution in the Nitro process. This issue is fixed in 3.21.10 and 4.5.1.

## References
- https://github.com/nuxt/nuxt/releases/tag/v3.21.10
- https://github.com/nuxt/nuxt/releases/tag/v4.5.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71320.json
- https://github.com/nuxt/nuxt/security/advisories/GHSA-9473-5f9j-94wq
- https://nvd.nist.gov/vuln/detail/CVE-2026-71320
- https://github.com/nuxt/nuxt/commit/5b60017f7f1d5e9384cadf1d6c580b99d583c418
- https://github.com/nuxt/nuxt/commit/ee6c846338f4eb75801815dda86df1f494725859
