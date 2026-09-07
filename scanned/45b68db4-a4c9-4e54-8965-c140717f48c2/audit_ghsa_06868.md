# [H] Craft CMS: DOM XSS via GitHub issue title in CraftSupport widget

## Summary
Severity: High
Advisory: GHSA-24x4-j6x9-rfw5
CVE: CVE-2026-55790
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-24x4-j6x9-rfw5
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.23
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.16

## Details
## Summary

An attacker with only a GitHub account can plant a JavaScript payload in a `craftcms/cms` issue title. When a Craft admin uses the CraftSupport widget’s "Give feedback" screen and types a search term that returns the poisoned issue, the payload executes in the admin’s control panel session.

No control panel account or elevated privileges are required on the attacker’s side.

## Preconditions

- Attacker has a GitHub account (no control panel access needed).
- Victim is an administrator, and you have the CraftSupport widget on the dashboard.
- Victim uses the "Give feedback" screen and types a search term that returns the poisoned issue.

## Root cause

`CraftSupportWidget.js` lines 382-392:

```js
$('<a>', {
  href: this.getSearchResultUrl(results[i]),
  target: '_blank',
  html:
    '<span class="status ' +
    this.getSearchResultStatus(results[i]) +
    '"></span>' +
    this.getSearchResultText(results[i]),
})
```

`FeedbackScreen.getSearchResultText` (line 669-671) returns `result.title` verbatim from the GitHub API response. The jQuery `html:` option sets the element’s `innerHTML`, so a title containing `<img src=x onerror=...>` executes immediately on render.

The GitHub API returns issue titles as raw JSON strings with no HTML encoding. The widget makes this request directly from the browser, without a Craft proxy or any sanitization step.

`HelpScreen` (Stack Exchange) is not affected because the Stack Exchange API HTML-encodes titles before returning them.

## Steps to reproduce

**Plant (attacker, GitHub account only):**

1. Open `https://github.com/craftcms/cms/issues/new`.
2. Set the title to a string combining a plausible search term and the payload, e.g.:

```
<img src=x onerror=alert(document.domain)> cannot upload files
```

3. Submit the issue.

**Trigger (victim, Craft admin):**

1. Open the Craft control panel dashboard.
2. Open the CraftSupport widget, click "Give feedback".
3. Type `cannot upload files` in the search box.
4. `alert(document.domain)` fires in the admin's session.

## Impact

XSS in the admin control panel session. The payload has access to `Craft.csrfTokenName` and `Craft.csrfTokenValue` and can send same-origin action requests as the admin without any further interaction.

## Mitigating factors

- Victim must actively use the "Give feedback" search screen.
- Attacker must predict or social-engineer a search term the admin will type, or use a broad term likely to match.
- Widget is only available to admins.

## Resources

https://github.com/craftcms/cms/commit/6bbb66038a268552180ca5c8eed9f46ea25a4417

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-24x4-j6x9-rfw5
- https://nvd.nist.gov/vuln/detail/CVE-2026-55790
- https://github.com/craftcms/cms/commit/6bbb66038a268552180ca5c8eed9f46ea25a4417
- https://github.com/craftcms/cms
