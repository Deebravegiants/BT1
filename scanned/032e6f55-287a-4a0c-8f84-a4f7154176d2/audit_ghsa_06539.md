# [C] MantisBT: Reflected XSS in admin/install.php

## Summary
Severity: Critical
Advisory: GHSA-77x8-3v3h-hrhv
CVE: CVE-2026-52847
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-77x8-3v3h-hrhv
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.28.4

## Details
MantisBT 2.28.3 and earlier contains six reflected XSS injection points in `/admin/install.php`. User-supplied parameters are echoed into HTML without escaping via print_test_result(). No authentication is required.

A Content Security Policy (script-src 'self') prevents inline JavaScript execution, but the CSP is missing a form-action directive, allowing exploitation via credential-phishing form injection and <meta> open redirects.

### Impact
- Credential phishing: Attacker crafts a URL that renders a fake login form on the real MantisBT admin page. Admin credentials are submitted to an attacker-controlled server.
- Open redirect: Victim is silently redirected to a phishing or malware site.
- UI manipulation: CSS injection can hide legitimate page content and overlay attacker-controlled HTML, enabling social engineering.

### Patches
- https://github.com/mantisbt/mantisbt/commit/0f32ceabadc745239754962df91a51d5d51e3fd7
- https://github.com/mantisbt/mantisbt/commit/f2191a0d8ce438bf74171d496cf721dae025a5c0

### Workarounds
Remove the `/admin` directory, as [recommended in the Admin Guide](https://mantisbt.org/docs/master/en-US/Admin_Guide/html-desktop/#admin.install.postcommon)

### Resources
- https://mantisbt.org/bugs/view.php?id=37103
- related advisory [GHSA-vcrw-4xvv-jh49](https://github.com/mantisbt/mantisbt/security/advisories/GHSA-vcrw-4xvv-jh49)

### Credits
McCaulay Hudson (@_McCaulay) of watchTowr

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-77x8-3v3h-hrhv
- https://github.com/mantisbt/mantisbt/commit/0f32ceabadc745239754962df91a51d5d51e3fd7
- https://github.com/mantisbt/mantisbt/commit/f2191a0d8ce438bf74171d496cf721dae025a5c0
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=37103
