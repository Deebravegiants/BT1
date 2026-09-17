# [M] Sulu grants access to pages regardless of role permissions

## Summary
Severity: Medium
Advisory: GHSA-jr83-m233-gg6p
CVE: CVE-2024-27915
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-03-04
Source: https://github.com/advisories/GHSA-jr83-m233-gg6p
Type: github-advisory

## Affected
- Packagist: `sulu/sulu` — affected >=2.2.0 <2.4.17
- Packagist: `sulu/sulu` — affected >=2.5.0-alpha1 <2.5.13

## Details
### Impact

_What kind of vulnerability is it? Who is impacted?_

Access to pages is granted regardless of role permissions for webspaces which have a security system configured and permission check enabled. Webspaces without do not have this issue.

### Patches

Has the problem been patched? What versions should users upgrade to?

The problem is patched with Version `2.4.17` and `2.5.13`.

### Workarounds

_Is there a way for users to fix or remediate the vulnerability without upgrading?_

Remove  following lines from `vendor/symfony/security-http/HttpUtils.php`:

```
-            // Shortcut if request has already been matched before
-            if ($request->attributes->has('_route')) {
-                return $path === $request->attributes->get('_route');
 -           }
```

Or do not install `symfony/security-http` versions greater equal than `v5.4.30` or `v6.3.6`.

### References

_Are there any links users can visit to find out more?_

Currently no references.

## References
- https://github.com/sulu/sulu/security/advisories/GHSA-jr83-m233-gg6p
- https://nvd.nist.gov/vuln/detail/CVE-2024-27915
- https://github.com/sulu/sulu/commit/ec9c3f99e15336dc4f6877f512300f231c17c6da
- https://github.com/sulu/sulu
