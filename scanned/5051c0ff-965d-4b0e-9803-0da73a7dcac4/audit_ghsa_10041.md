# [H] @payloadcms/next has Stored XSS in Admin Panel

## Summary
Severity: High
Advisory: GHSA-mmxc-95ch-2j7c
CVE: CVE-2026-34748
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-mmxc-95ch-2j7c
Type: github-advisory

## Affected
- npm: `@payloadcms/next` — affected >=0 <3.78.0

## Details
### Impact

A stored Cross-site Scripting (XSS) vulnerability existed in the admin panel. An authenticated user with write access to a collection could save content that, when viewed by another user, would execute in their browser.

Consumers are affected if ALL of these are true:

- Payload version **< v3.78.0**
- At least one collection with versions enabled
- An authenticated user has `create` or `update` access to that collection

### Patches

This vulnerability has been patched in **v3.78.0**. Output encoding has been added to prevent user-supplied content from being interpreted as markup.

Users should upgrade to **v3.78.0** or later.

### Workarounds

If consumers cannot upgrade immediately:

- Restrict `create` and `update` access to versioned collections to trusted roles only.

## References
- https://github.com/payloadcms/payload/security/advisories/GHSA-mmxc-95ch-2j7c
- https://nvd.nist.gov/vuln/detail/CVE-2026-34748
- https://github.com/payloadcms/payload
