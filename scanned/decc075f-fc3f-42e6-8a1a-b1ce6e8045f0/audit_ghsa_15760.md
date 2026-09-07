# [H] Plate media plugins has a XSS in media embed element when using custom URL parsers

## Summary
Severity: High
Advisory: GHSA-h3pq-667x-r789
CVE: CVE-2024-40631
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-07-15
Source: https://github.com/advisories/GHSA-h3pq-667x-r789
Type: github-advisory

## Affected
- npm: `@udecode/plate-media` — affected >=0 <36.0.10

## Details
### Impact
Editors that use `MediaEmbedElement` and pass custom `urlParsers` to the `useMediaState` hook may be vulnerable to XSS if a custom parser allows `javascript:`, `data:` or `vbscript:` URLs to be embedded. Editors that do not use `urlParsers` and instead consume the `url` property directly may also be vulnerable if the URL is not sanitised.

The default parsers `parseTwitterUrl` and `parseVideoUrl` are not affected.

Examples of vulnerable code:

```tsx
const { embed } = useMediaState({
  urlParsers: [
    // Custom parser that does not use an allowlist or validate the URL protocol
    (url) => ({ url }),
  ],
});

return (
  <iframe
    src={embed!.url}
    // ...
  />
);
```

```tsx
const { url } = useMediaState();

return (
  <iframe
    // url property used directly from useMediaState() with no sanitisation
    src={url}
    // ...
  />
);
```


```tsx
const { url } = element;

return (
  <iframe
    // url property used directly from element with no sanitisation
    src={url}
    // ...
  />
);
```

### Patches
`@udecode/plate-media` 36.0.10 resolves this issue by only allowing HTTP and HTTPS URLs during parsing. This affects only the `embed` property returned from `useMediaState`.

In addition, the `url` property returned from `useMediaState` has been renamed to `unsafeUrl` to indicate that it has not been sanitised. The `url` property on `element` is also unsafe, but has not been renamed. If you're using either of these properties directly, you will still need to validate the URL yourself.

### Workarounds
Ensure that any custom `urlParsers` do not allow `javascript:`, `data:` or `vbscript:` URLs to be returned in the `url` property of their return values.

If `url` is consumed directly, validate the URL protocol before passing it to the `iframe` element.

### References
How to verify the protocol of a URL: https://stackoverflow.com/a/43467144

## References
- https://github.com/udecode/plate/security/advisories/GHSA-h3pq-667x-r789
- https://nvd.nist.gov/vuln/detail/CVE-2024-40631
- https://github.com/udecode/plate/commit/1bc0971774fbfb770780c9bdb94746a6f0f196a0
- https://github.com/udecode/plate
- https://stackoverflow.com/a/43467144
