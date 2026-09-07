# [H] YAFNET has Stored XSS in Forum Thread Posts/Replies that Allows Arbitrary JavaScript Execution for All Thread Viewers

## Summary
Severity: High
Advisory: GHSA-8rq5-wwpp-fmj2
CVE: CVE-2026-43939
CWE: CWE-116, CWE-79, CWE-80
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-8rq5-wwpp-fmj2
Type: github-advisory

## Affected
- NuGet: `YAFNET.Core` — affected >=4.0.0-beta01 <4.0.5
- NuGet: `YAFNET.Core` — affected >=0 <3.2.12

## Details
**Description:**
Stored Cross-Site Scripting (XSS) occurs when user-supplied input is persisted by the application and later rendered in another user's browser without proper sanitization or contextual output encoding. When the vulnerable sink is a high-traffic surface such as a public forum thread, the payload executes in the browser of every user who visits the page, maximizing both reach and impact. Any JavaScript injected through such a sink runs under the application's origin and inherits the privileges of whichever user happens to view the affected content.

**Issue Details:**
The thread posting and reply feature accepts user-supplied content that is stored server-side and later rendered back into the thread page without adequate HTML sanitization or contextual output encoding. Submitting a post or reply containing `"><img src=x onerror=prompt(0)>` causes the payload to break out of the surrounding HTML context and inject a fully attacker-controlled `<img>` element whose `onerror` handler fires automatically as soon as the broken image reference fails to load. Because posts and replies are visible to every user who visits the thread, authenticated or otherwise, the injected JavaScript executes in each viewer's browser the moment the page renders, with no additional interaction required.

**Impact:**
An attacker with a standard forum account can execute arbitrary JavaScript in the browser of every user who loads the affected thread, including moderators and administrators. This enables session/auth-cookie theft, account takeover through same-origin state-changing requests, forced privileged actions if an administrator views the thread, credential phishing via injected login overlays, forum defacement, cryptominer or malware delivery, and mass redirection of viewers to attacker-controlled sites. Because the payload triggers automatically on page load rather than requiring hover or click interaction, a single malicious post can compromise a large number of users very quickly.

**Likelihood:**
Exploitation requires only a registered account with permission to post or reply, which is available to every forum member by default. Once posted, the payload fires automatically for any visitor who opens the thread, requiring zero victim interaction and making the overall likelihood high.

**Steps to Reproduce:**
- Log in to the forum as any low-privileged user (Attacker).
- Navigate to any thread where posting or replying is allowed, or create a new thread.
- In the post/reply body, submit the payload: `"><img src=x onerror=prompt(0)>`
- Publish the post or reply.
- Log in as a different user (e.g., Admin) or visit the thread in a separate browser session.
- Open the thread page, the injected `<img>` fails to load and the `onerror` handler fires, producing a `prompt(0)` dialog and confirming arbitrary JavaScript execution in the viewer's session context.
<img width="1127" height="745" alt="image" src="https://github.com/user-attachments/assets/b93442ea-1d8e-4079-ab4f-e52d41d110f3" />

## References
- https://github.com/YAFNET/YAFNET/security/advisories/GHSA-8rq5-wwpp-fmj2
- https://nvd.nist.gov/vuln/detail/CVE-2026-43939
- https://github.com/YAFNET/YAFNET
- https://github.com/YAFNET/YAFNET/releases/tag/v3.2.12
- https://github.com/YAFNET/YAFNET/releases/tag/v4.0.5
