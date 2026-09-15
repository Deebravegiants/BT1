# [M] flarum/nicknames extension has display name injection in notification emails (autolink & markdown)

## Summary
Severity: Medium
Advisory: GHSA-3c4m-j3g4-hh25
CVE: CVE-2026-30913
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-3c4m-j3g4-hh25
Type: github-advisory

## Affected
- Packagist: `flarum/nicknames` — affected >=0 <1.8.3

## Details
## Summary

When the `flarum/nicknames` extension is enabled, a registered user can set their nickname to a string that email clients interpret as a hyperlink. The nickname is inserted verbatim into plain-text notification emails, and recipients may be misled into visiting attacker-controlled domains.

## Affected package

- **`flarum/nicknames`** — permissive display name driver that allows special characters; affected since initial release on the `1.x` branch

Any third-party display name driver that permits special characters would be equally affected.

## Variants

1. **Domain autolink** — a nickname such as `nasty.com` is automatically converted to a clickable hyperlink by virtually all email clients (Gmail, Outlook, Apple Mail, Thunderbird).
2. **Markdown link syntax** — a nickname such as `[CLICK](https://evil.com)` is rendered as a clickable hyperlink by email clients that auto-render markdown in plain-text emails (e.g. Apple Mail, Thunderbird).

## Steps to reproduce

**Variant 1 (autolink — affects all email clients)**
1. Enable `flarum/nicknames`, set nickname to `nasty.com`
2. Trigger a notification email to another user (e.g. follow them, mention them)
3. The nickname appears as a clickable link in the received email

**Variant 2 (markdown — affects markdown-rendering email clients)**
1. Enable `flarum/nicknames`, set nickname to `[CLICK](https://evil.com)`
2. Trigger a notification email to another user
3. In a markdown-rendering email client (e.g. Apple Mail), the nickname appears as a clickable link

## Impact

Phishing / social engineering: victims may be misled into visiting attacker-controlled URLs via links appearing to originate from a trusted platform notification email. Variant 1 is exploitable against virtually all email clients without any special conditions.

- CVSS v3.1: `AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N` — **4.6 Medium**

## Root cause

The default username-based display name driver constrains values to `[a-zA-Z0-9_-]+`, making it immune. `flarum/nicknames` introduced permissive validation (min/max length and an optional admin-configured regex) that allows arbitrary characters including those meaningful in URL and markdown contexts. This has been the case since the first commit of the extension.

## Proposed fix

- Add validation in `flarum/nicknames` to reject or sanitize nicknames containing characters that email clients may interpret as URLs or markdown links
- Alternatively, sanitize the display name before insertion into notification email bodies so that legitimate nicknames like `Jane.Smith` are preserved but rendered safely

## References

- Bug bounty submission: SBB-L4ZVAFH8 (Intigriti)

## References
- https://github.com/flarum/framework/security/advisories/GHSA-3c4m-j3g4-hh25
- https://nvd.nist.gov/vuln/detail/CVE-2026-30913
- https://github.com/flarum/nicknames/commit/4dde99729abdce8f6e2a7437c86e38735fdcca28
- https://github.com/flarum/framework
- https://github.com/flarum/nicknames/releases/tag/v1.8.
- https://github.com/flarum/nicknames/releases/tag/v1.8.3
