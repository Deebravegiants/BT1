# [M] Isso affected by Stored XSS via comment website field

## Summary
Severity: Medium
Advisory: GHSA-9fww-8cpr-q66r
CVE: CVE-2026-27469
CWE: CWE-116, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-9fww-8cpr-q66r
Type: github-advisory

## Affected
- PyPI: `isso` — affected >=0 <0.13.2

## Details
## Impact

This is a stored Cross-Site Scripting (XSS) vulnerability affecting the website and author comment fields. The website field was HTML-escaped using quote=False, which left single and double quotes unescaped. Since the frontend inserts the website value directly into a single-quoted href attribute via string concatenation, a single quote in the URL breaks out of the attribute context, allowing injection of arbitrary event handlers (e.g. onmouseover, onclick).

The same escaping was missing entirely from the user-facing comment edit endpoint (PUT /id/<id>) and the moderation edit endpoint (POST /id/<id>/edit/<key>).

Any visitor to a page embedding isso comments is impacted. No authentication or interaction beyond mouse movement is required to trigger a payload — an attacker can post a comment anonymously (moderation is off by default) with a crafted website URL, and the payload persists in the database and fires on every page load. With the full-page invisible overlay technique described in the report, the victim only needs to move their mouse.

## Patches

The issue is fixed in commit 3cf27c2. Users should upgrade to a version containing that commit once released. The fix applies html.escape(..., quote=True) to the website field across all three write paths (POST /new, PUT /id/<id>, POST /id/<id>/edit/<key>), and adds input validation and escaping to the moderation edit endpoint which previously had neither.

## Workarounds

  Enabling comment moderation (moderation = enabled = true in isso.cfg) prevents unauthenticated users from publishing comments, raising the bar for exploitation. However, it
  does not fully mitigate the issue since a moderator activating a malicious comment would still expose visitors. There is no configuration-only workaround that fully prevents
   the vulnerability.

## Resources

  - https://docs.python.org/3/library/html.html#html.escape — note the quote parameter

## References
- https://github.com/isso-comments/isso/security/advisories/GHSA-9fww-8cpr-q66r
- https://nvd.nist.gov/vuln/detail/CVE-2026-27469
- https://github.com/isso-comments/isso/commit/0afbfe0691ee237963e8fb0b2ee01c9e55ca2144
- https://docs.python.org/3/library/html.html#html.escape
- https://github.com/isso-comments/isso
