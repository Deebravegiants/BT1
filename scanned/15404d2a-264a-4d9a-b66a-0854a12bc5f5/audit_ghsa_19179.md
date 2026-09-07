# [H] Solid Lacks Escaping of HTML in JSX Fragments allows for Cross-Site Scripting (XSS)

## Summary
Severity: High
Advisory: GHSA-3qxh-p7jc-5xh6
CVE: CVE-2025-27109
CWE: CWE-116, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-02-25
Source: https://github.com/advisories/GHSA-3qxh-p7jc-5xh6
Type: github-advisory

## Affected
- npm: `solid-js` — affected >=0 <1.9.4

## Details
Inserts/JSX expressions inside illegal inlined JSX fragments lacked escaping, allowing user input to be rendered as HTML when put directly inside JSX fragments.

For instance, `?text=<svg/onload=alert(1)>` would trigger XSS here.
```js
  const [text] = createResource(() => {
    return new URL(getRequestEvent().request.url).searchParams.get("text");
  });

  return (
    <>
      Text: {text()}
    </>
  );
  ```

## References
- https://github.com/solidjs/solid/security/advisories/GHSA-3qxh-p7jc-5xh6
- https://nvd.nist.gov/vuln/detail/CVE-2025-27109
- https://github.com/solidjs/solid/commit/b93956f28ed75469af6976a98728e313d0edd236
- https://github.com/solidjs/solid
