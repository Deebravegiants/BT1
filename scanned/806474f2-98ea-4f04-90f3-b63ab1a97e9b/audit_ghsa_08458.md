# [M] AVideo CVE-2026-43881 incomplete fix - `objects/mention.json.php:17` is an unauthenticated user enumeration sibling that survives `d9cdc7024`

## Summary
Severity: Medium
Advisory: GHSA-vpfx-pxqw-2w79
CVE: CVE-2026-45620
CWE: CWE-204, CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-vpfx-pxqw-2w79
Type: github-advisory

## Affected
- Packagist: `WWBN/AVideo` — affected >=0

## Details
CVE-2026-43881 fix `d9cdc7024` patched `users.json.php` only. The same anti-pattern survives at master HEAD in:

```
objects/mention.json.php:17     $ignoreAdmin = true;
objects/mention.json.php:18     $users = User::getAllUsers($ignoreAdmin,
                                    ['name', 'email', 'user', 'channelName'], 'a');
```

No `User::loginCheck()`, no admin gate. Only entry guard: `preg_match('/^@/', $_REQUEST['term'])` and hard-coded `rowCount=10`.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-vpfx-pxqw-2w79
- https://nvd.nist.gov/vuln/detail/CVE-2026-45620
- https://github.com/WWBN/AVideo
- https://github.com/advisories/GHSA-6rvw-7p8v-mjfq
