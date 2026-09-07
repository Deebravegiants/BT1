# [M] vue-i18n's escapeParameterHtml does not prevent DOM-based XSS through its tag attributes

## Summary
Severity: Medium
Advisory: GHSA-x8qp-wqqm-57ph
CVE: CVE-2025-53892
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-07-16
Source: https://github.com/advisories/GHSA-x8qp-wqqm-57ph
Type: github-advisory

## Affected
- npm: `vue-i18n` — affected >=9.0.0 <9.14.5
- npm: `vue-i18n` — affected >=10.0.0 <10.0.8
- npm: `vue-i18n` — affected >=11.0.0 <11.1.10
- npm: `@intlify/core` — affected >=9.0.0 <9.14.5
- npm: `@intlify/core` — affected >=10.0.0 <10.0.8
- npm: `@intlify/core` — affected >=11.0.0 <11.1.10
- npm: `@intlify/core-base` — affected >=9.0.0 <9.14.5
- npm: `@intlify/core-base` — affected >=10.0.0 <10.0.8
- npm: `@intlify/core-base` — affected >=11.0.0 <11.1.10
- npm: `@intlify/vue-i18n-core` — affected >=9.2.0 <9.14.5
- npm: `@intlify/vue-i18n-core` — affected >=10.0.0 <10.0.8
- npm: `@intlify/vue-i18n-core` — affected >=11.0.0 <11.1.10
- npm: `petite-vue-i18n` — affected >=10.0.0 <10.0.8
- npm: `petite-vue-i18n` — affected >=11.0.0 <11.1.10

## Details
### Summary
The escapeParameterHtml: true option in Vue I18n is designed to protect against HTML/script injection by escaping interpolated parameters. However, this setting fails to prevent execution of certain tag-based payloads, such as `<img src=x onerror=...>`, if the interpolated value is inserted inside an HTML context using v-html.

This may lead to a DOM-based XSS vulnerability, even when using escapeParameterHtml: true, if a translation string includes minor HTML and is rendered via v-html.

### Details

When escapeParameterHtml: true is enabled, it correctly escapes common injection points.

However, it does not sanitize entire attribute contexts, which can be used as XSS vectors via:

`<img src=x onerror=alert(1)>
`
### PoC
In your Vue I18n configuration:

```
const i18n = createI18n({
  escapeParameterHtml: true,
  messages: {
    en: {
      vulnerable: 'Caution: <img src=x onerror="{payload}">'
    }
  }
});
```
Use this interpolated payload:

`const payload = '<script>alert("xss")</script>';`
Render the translation using v-html (even not using v-html):

`<p v-html="$t('vulnerable', { payload })"></p>
`
Expected: escaped content should render as text, not execute.

Actual: script executes in some environments (or the payload is partially parsed as HTML).

### Impact

This creates a DOM-based Cross-Site Scripting (XSS) vulnerability despite enabling a security option (escapeParameterHtml) .

## References
- https://github.com/intlify/vue-i18n/security/advisories/GHSA-x8qp-wqqm-57ph
- https://nvd.nist.gov/vuln/detail/CVE-2025-53892
- https://github.com/intlify/vue-i18n/pull/2229
- https://github.com/intlify/vue-i18n/pull/2230
- https://github.com/intlify/vue-i18n/commit/49f982443ab8fd94ecc427b265ce97d57df94d7e
- https://github.com/intlify/vue-i18n/commit/a47099619fb9b256e86341a8658ebe72e92ab099
- https://github.com/intlify/vue-i18n
- https://github.com/intlify/vue-i18n/releases/tag/v10.0.8
- https://github.com/intlify/vue-i18n/releases/tag/v11.1.10
- https://github.com/intlify/vue-i18n/releases/tag/v9.14.5
