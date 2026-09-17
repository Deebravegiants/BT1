# [M] Astro has an Authentication Bypass via Double URL Encoding, a bypass for CVE-2025-64765

## Summary
Severity: Medium
Advisory: GHSA-whqg-ppgf-wp8c
CVE: CVE-2025-66202
CWE: CWE-647
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-whqg-ppgf-wp8c
Type: github-advisory

## Affected
- npm: `astro` — affected >=0 <5.15.8

## Details
# Authentication Bypass via Double URL Encoding in Astro
## Bypass for CVE-2025-64765 / GHSA-ggxq-hp9w-j794

---

### Summary

A **double URL encoding bypass** allows any unauthenticated attacker to bypass path-based authentication checks in Astro middleware, granting unauthorized access to protected routes. While the original CVE-2025-64765 (single URL encoding) was fixed in v5.15.8, the fix is insufficient as it only decodes once. By using double-encoded URLs like `/%2561dmin` instead of `/%61dmin`, attackers can still bypass authentication and access protected resources such as `/admin`, `/api/internal`, or any route protected by middleware pathname checks.


## Fix 

A more secure fix is just decoding once, then if the request has a %xx format, return a 400 error by using something like :

```
if (containsEncodedCharacters(pathname)) {
            // Multi-level encoding detected - reject request
            return new Response(
                'Bad Request: Multi-level URL encoding is not allowed',
                {
                    status: 400,
                    headers: { 'Content-Type': 'text/plain' }
                }
            );
        }
```

## References
- https://github.com/withastro/astro/security/advisories/GHSA-ggxq-hp9w-j794
- https://github.com/withastro/astro/security/advisories/GHSA-whqg-ppgf-wp8c
- https://nvd.nist.gov/vuln/detail/CVE-2025-64765
- https://nvd.nist.gov/vuln/detail/CVE-2025-66202
- https://github.com/withastro/astro/commit/6f800813516b07bbe12c666a92937525fddb58ce
- https://github.com/withastro/astro
