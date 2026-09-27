# [M] Craft CMS: Stored XSS via Structure entry title in table view

## Summary
Severity: Medium
Advisory: GHSA-xrqc-p465-2xvg
CVE: CVE-2026-55793
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-xrqc-p465-2xvg
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.53

## Details
# Stored XSS via Structure entry title in table view

## Summary

An Author-level control panel user can store a JavaScript payload in an entry title. When an admin, or any control panel user with `saveEntries` for the same Structure section, drags another entry under the poisoned entry in table view, the payload executes in the victim’s session.

The issue is exploitable because the title is escaped into `data-title` by the server, decoded again by the browser, read with jQuery `.data('title')`, and then concatenated into a new HTML string without attribute escaping.

Execution was verified with `alert(document.domain)`. Impact was verified against an elevated admin session by changing the admin user’s email through `users/save-user`, then using the password-reset flow to take over the account.

## Preconditions

- Attacker has `createEntries` + `saveEntries` on a Structure-type section (Author-style CP account; no admin permission required).
- Victim has `saveEntries` on the same section. Craft only renders drag handles when `structureEditable` is true, which requires this permission, so any admin qualifies.
- Section must be type Structure. Channel and Single sections are unaffected.
- Poisoned entry must have no children at the time of the drag (fires on the 0-to-1 descendant transition).
- For the email-change account-takeover path, the victim must currently have an elevated session. The stored XSS itself does not require elevation.

## Root cause

`ElementTableSorter.js` lines 643-652:

```js
const ancestorTitle = this._updateAncestors._$ancestor.data('title');
$(
  '<button … aria-label="' +
    Craft.t('app', 'Show {title} children', {title: ancestorTitle}) +
  '"></button>'
).insertAfter(…);
```

`Craft.t` with a `{title}` token calls `_parseToken`, reaches `case 'none': return arg` (`Craft.js:193-194`), and returns the title verbatim. The result is handed to jQuery's `$()` and parsed as HTML.

The server-side template correctly encodes the entry title into `data-title`, but the browser decodes that attribute before jQuery returns it from `.data('title')`. At that point the value is attacker-controlled HTML, and it is inserted into the `aria-label` attribute without `Craft.escapeHtml()`.

## Steps to reproduce

**Plant (attacker - Author account):**

```bash
python3 poc.py --url http://target --cp admin \
  --user author@example.com --pass secret --section mySection
```

**Trigger (victim - any control panel user with `saveEntries`, e.g. admin):**

1. Open the section index in Table view.
2. Drag the "Drag me" entry and drop it as the first child of the poisoned entry.

`alert(document.domain)` fires in the victim’s session.

**Impact payload tested in an elevated admin session (249 chars, within the 255-char title limit):**

```html
"><img src=x onerror="fetch(Craft.actionUrl+'users/save-user',{method:'POST',body:Craft.csrfTokenName+'='+encodeURIComponent(Craft.csrfTokenValue)+'&userId=1&email=attacker%40evil.com',headers:{'Content-Type':'application/x-www-form-urlencoded'}})">
```

When triggered during an elevated admin session, the admin’s email is changed to the attacker-controlled address. The attacker can then request a password reset and receive the reset link.

## Impact

Stored XSS in the control panel from an Author-level account. The payload runs as the victim control panel user and can use `Craft.csrfTokenName` / `Craft.csrfTokenValue` to send same-origin action requests as that user.

In my test environment, triggering the payload in an elevated admin session allowed Author-to-admin account takeover via admin email change and password reset.

## Mitigating factors

- Requires an existing control panel account (Author role minimum).
- Victim must perform a drag operation, not just visit the page.
- The demonstrated email-change takeover requires the victim’s session to be elevated at trigger time.

## Resources

https://github.com/craftcms/cms/commit/162321e899cc97517fb6f5a02b5528f549d0c6cc

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-xrqc-p465-2xvg
- https://nvd.nist.gov/vuln/detail/CVE-2026-55793
- https://github.com/craftcms/cms/commit/162321e899cc97517fb6f5a02b5528f549d0c6cc
- https://github.com/craftcms/cms
