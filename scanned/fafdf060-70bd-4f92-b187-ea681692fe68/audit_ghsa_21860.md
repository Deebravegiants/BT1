# [M] Improper CSP in Image Optimization API for Next.js versions between 10.0.0 and 12.1.0

## Summary
Severity: Medium
Advisory: GHSA-fmvm-x8mv-47mj
CVE: CVE-2022-23646
CWE: CWE-451
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-17
Source: https://github.com/advisories/GHSA-fmvm-x8mv-47mj
Type: github-advisory

## Affected
- npm: `next` — affected >=10.0.0 <12.1.0

## Details
Next.js is a React framework. Starting with version 10.0.0 and prior to version 12.1.0, Next.js is vulnerable to User Interface (UI) Misrepresentation of Critical Information. In order to be affected, the `next.config.js` file must have an `images.domains` array assigned and the image host assigned in `images.domains` must allow user-provided SVG. If the `next.config.js` file has `images.loader` assigned to something other than default, the instance is not affected. Version 12.1.0 contains a patch for this issue. As a workaround, change `next.config.js` to use a different `loader configuration` other than the default.

### Impact
- **Affected**: All of the following must be true to be affected
  - Next.js between version 10.0.0 and 12.0.10
  - The `next.config.js` file has [images.domains](https://nextjs.org/docs/api-reference/next/image#domains) array assigned
  - The image host assigned in [images.domains](https://nextjs.org/docs/api-reference/next/image#domains) allows user-provided SVG
- **Not affected**: The `next.config.js` file has [images.loader](https://nextjs.org/docs/api-reference/next/image#loader-configuration) assigned to something other than default

### Patches
[Next.js 12.1.0](https://github.com/vercel/next.js/releases/tag/v12.1.0)

### Workarounds
Change `next.config.js` to use a different [loader configuration](https://nextjs.org/docs/api-reference/next/image#loader-configuration) other than the default, for example:

```js
module.exports = {
  images: {
    loader: 'imgix',
    path: 'https://example.com/myaccount/',
  },
}
```

Or if you want to use the [`loader`](https://nextjs.org/docs/api-reference/next/image#loader) prop on the component, you can use `custom`:
```js
module.exports = {
  images: {
    loader: 'custom',
  },
}
```

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-fmvm-x8mv-47mj
- https://nvd.nist.gov/vuln/detail/CVE-2022-23646
- https://github.com/vercel/next.js/pull/34075
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v12.1.0
