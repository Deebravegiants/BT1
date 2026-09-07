# [H] Novu has a XSS sanitization bypass

## Summary
Severity: High
Advisory: GHSA-26wg-9xf2-q495
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-26wg-9xf2-q495
Type: github-advisory

## Affected
- npm: `novu/api` — affected >=0 <3.15.0

## Details
### Summary

XSS sanitization is incomplete, some attributes are missing such as `oncontentvisibilityautostatechange=`. This allows for the email preview to render HTML that executes arbitrary JavaScript,

### Details

Sanitization is implemented here:
https://github.com/novuhq/novu/blob/next/libs/application-generic/src/services/sanitize/sanitizer.service.ts

With `allowedAttributes: false`, all attributes are allowed through `sanitize-html`. Even dangerous ones like `oncontentvisibilityautostatechange=`. The `DANGEROUS_ATTRIBUTES` array tries to handle this by denying more attributes after the fact, but this list is incomplete. I copied all well-known payloads from:
https://portswigger.net/web-security/cross-site-scripting/cheat-sheet
And found that the `oncontentvisibilityautostatechange=` attribute isn't detected. 

PS. there seems to also be another even more lax sanitizer here, but I wasn't able to figure out where it is used:
https://github.com/novuhq/novu/blob/next/packages/framework/src/utils/sanitize.utils.ts

### PoC

1. Create a new workflow and add an *Email* step
2. In the body, write the following HTML code:

```html
<a oncontentvisibilityautostatechange="alert(window.origin)" style="display:block;content-visibility:auto">
```

3. Wait a second and notice the XSS popup showing the current origin:

<img width="1515" height="610" alt="image" src="https://github.com/user-attachments/assets/7d519a50-3bed-4f04-b78c-9c5938717433" />

https://dashboard.novu.co/env/dev_env_gVtdgDEhgf1CetwX/workflows/onboarding-demo-workflow_wf_gVtdh2uV0h7j3ffK/steps/email-step_st_gVtqdgIrOkYVvP9F/editor

### Impact

This may look like a Self-XSS similar to https://github.com/novuhq/novu/security/advisories/GHSA-w8vm-jx29-52fr, but it can be more impactful. First of all, if multiple users can access this dashboard, the link above can directly bring the to the email step editor to trigger the XSS.
An attacker can also use the Google/GitHub OAuth flows without completing the code callback step, and send that URL to the victim to intentionally log the vicitm into the attacker's account. If the attacker has prepared an XSS payload there, they will now be allowed to view it, so it triggers.

## References
- https://github.com/novuhq/novu/security/advisories/GHSA-26wg-9xf2-q495
- https://github.com/novuhq/novu
