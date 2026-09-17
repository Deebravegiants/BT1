# [M] tarteaucitron: data-cookie attribute can be used to delete arbitrary cookies

## Summary
Severity: Medium
Advisory: GHSA-jxj7-g6gm-49j7
CVE: CVE-2026-49977
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-jxj7-g6gm-49j7
Type: github-advisory

## Affected
- npm: `tarteaucitronjs` — affected >=0 <1.33.0

## Details
### Summary

tarteaucitron provides a list of cookies and buttons to delete them. If an attacker can write HTML with data attributes, they could create an element that silently deletes a cookie when clicked and trick a user to delete this cookie.

### Details

`tarteaucitron.cookie.purge()` is called on any element with the `purgeBtn` class. It does not check if the element is a legitimate tarteaucitron button or if the cookie corresponds to a service handled by tarteaucitron.

### PoC

```html
<a class="purgeBtn" data-cookie="foo">Click me!</a>
```

If someone has a cookie with this name and clicks on the link, the cookie is silently deleted.

### Impact

The impact is limited because this only works on cookies without HttpOnly=true and the attacker has to know the name of the cookie.

## References
- https://github.com/AmauriC/tarteaucitron.js/security/advisories/GHSA-jxj7-g6gm-49j7
- https://github.com/AmauriC/tarteaucitron.js
