# [M] Emissary has Stored XSS via Navigation Template Link Injection

## Summary
Severity: Medium
Advisory: GHSA-cpm7-cfpx-3hvp
CVE: CVE-2026-35571
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-cpm7-cfpx-3hvp
Type: github-advisory

## Affected
- Maven: `gov.nsa.emissary:emissary` — affected >=0 <8.39.0

## Details
## Summary

Mustache navigation templates interpolated configuration-controlled link values
directly into `href` attributes without URL scheme validation. An administrator
who could modify the `navItems` configuration could inject `javascript:` URIs,
enabling stored cross-site scripting (XSS) against other authenticated users
viewing the Emissary web interface.

## Details

### Vulnerable code — `nav.mustache` (line 10)

```html
{{#navItems}}
<li class="nav-item">
  <a class="nav-link" href="{{link}}">{{display}}</a>
</li>
{{/navItems}}
```

The `{{link}}` value was rendered without any scheme validation. Mustache's
default HTML escaping protects against injection of new HTML tags but does
**not** prevent `javascript:` URIs in `href` attributes, since `javascript:`
contains no characters that HTML-escaping would alter.

### Attack vector

An administrator sets a navigation item's link to:
```
javascript:alert(document.cookie)
```

Any authenticated user who clicks the navigation link executes the script in
their browser context.

### Impact

- Session hijacking via cookie theft
- Actions performed on behalf of the victim user
- Requires administrative access to modify navigation configuration
- Requires user interaction (clicking the malicious link)

### Mitigating factors

- Exploitation requires administrative access to modify the `navItems`
  configuration
- User interaction (clicking the link) is required
- The Emissary web interface is typically accessed only by authenticated
  operators within a trusted network

## Remediation

Fixed in [PR #1293](https://github.com/NationalSecurityAgency/emissary/pull/1293),
merged into release 8.39.0.

### Server-side link validation — `NavAction.java`

An allowlist regex was added that only permits `http://`, `https://`, or
site-relative (`/`) URLs:

```java
private static final Pattern VALID_LINK = Pattern.compile("^(https?:/)?/.*");

private static boolean isValidLink(String link) {
    if (!VALID_LINK.matcher(link).matches()) {
        logger.warn("Skipping invalid navigation link '{}'", link);
        return false;
    }
    return true;
}
```

Invalid links are logged and silently dropped from the rendered navigation.

### Template hardening — `nav.mustache`

Added `rel="noopener noreferrer"` to all navigation link anchor tags as a
defense-in-depth measure:

```html
<a class="nav-link" href="{{link}}" rel="noopener noreferrer">{{display}}</a>
```

Tests were added to verify that `javascript:` and `ftp://` URIs are rejected
while `http://`, `https://`, and site-relative (`/path`) links are accepted.

## Workarounds

If upgrading is not immediately possible, audit the navigation configuration
to ensure all `navItems` link values use only `http://`, `https://`, or
relative (`/`) URL schemes.

## References

- [PR #1293 — validate nav links](https://github.com/NationalSecurityAgency/emissary/pull/1293)
- Original report: GHSA-wjqm-p579-x3ww

## References
- https://github.com/NationalSecurityAgency/emissary/security/advisories/GHSA-cpm7-cfpx-3hvp
- https://nvd.nist.gov/vuln/detail/CVE-2026-35571
- https://github.com/NationalSecurityAgency/emissary/pull/1293
- https://github.com/NationalSecurityAgency/emissary/commit/e2078417464b9004620dde28dcbca2f73ea06c13
- https://github.com/NationalSecurityAgency/emissary
