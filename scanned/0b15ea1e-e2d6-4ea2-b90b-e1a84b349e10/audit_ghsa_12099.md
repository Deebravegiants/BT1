# [H] Craft CMS Vulnerable to Privilege Escalation/Bypass through UsersController->actionImpersonateWithToken()

## Summary
Severity: High
Advisory: GHSA-cc7p-2j3x-x7xf
CVE: CVE-2026-32267
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-cc7p-2j3x-x7xf
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.6
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.12

## Details
### Summary
A low-privilege user (or an unauthenticated user who has been sent a shared URL) can escalate their privileges to admin by abusing `UsersController->actionImpersonateWithToken`.

Affected users should update to Craft 4.17.6 and 5.9.12 to mitigate the issue.

### Details
This vulnerability allows any low-privilege user to escalate their privileges and become an admin, or, in extreme circumstances, unprivileged users to do the same.

Therefore, this vulnerability affects Craft Pro and Team more than Craft Solo.

Specifically, an attacker who possesses a valid “preview token” can then append `&action=users/impersonate-with-token&userId=1&prevUserId=1` to the preview URL to hijack the request into the impersonation endpoint, logging in as any user (including admin) without authentication. Getting the preview token is easy, and all an editor would have to do is create a single article, click “Preview”, and then recover this token.

Here’s what happens:

1. The action re-dispatch in `actionPreview()` passes `$skipSpecialHandling=true` to `handleRequest()`, bypassing all security guards, and passes `$checkToken=false` to `checkIfActionRequest()`, which allows an attacker-controlled action query parameter to override the dispatch target.
2. The `requireToken()` guard on `actionImpersonateWithToken()` only checks a boolean (`_hadToken`) that was set when the preview token was initially resolved. It does not verify that the token was intended for the impersonation action, and so any valid token from any route satisfies the check.
3. `actionImpersonateWithToken` is listed in `$allowAnonymous` and performs no authorization beyond `requireToken()`, so no prior authentication is required.

### PoC

The PoC achieves full admin takeover on the latest Craft CMS 5.9.10. Spawn a local version of Craft. Then, you’ll want to log in and create a valid setup:

1. Log in at http://host:18895/admin
2. Go to Settings,  Sections, New Section (name: "Blog", type: "Channel")
3. Under Site Settings, set URI Format to blog/{slug}
4. Then go to Entries, New Entry, Blog, and give it any title

Next, obtain a preview token

1. Open the saved entry in the editor
2. Click the Preview button
3. A preview pane opens with the entry rendered in an iframe
4. Right-click inside the preview pane and Inspect Element
5. Find the <iframe> element; its src contains the tokenized URL: `http://host:18895/blog/title?x-craft-live-preview=...&token=XXXXXXXX`
6. Copy the `token=` value

Finally, execute the exploit:

  1. Open a new incognito/private browser window
  2. Navigate to: `http://host:18895/?token=XXXXXXXX&action=users/impersonate-with-token&userId=1&prevUserId=1`
  3. You may see a 404.  This is expected.

To verify the exploit, in the same incognito tab, navigate to `http://host:18895/admin`. You should land on the admin dashboard, logged in as admin, without ever entering credentials.

### Impact

Privilege escalation; everyone is impacted.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-cc7p-2j3x-x7xf
- https://nvd.nist.gov/vuln/detail/CVE-2026-32267
- https://github.com/craftcms/cms/commit/6301e217c5f15617d939c432cb770db50af14b33
- https://github.com/craftcms/cms
