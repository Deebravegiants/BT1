# [H] EasyAdmin: Stored Cross-Site Scripting (XSS) via uploaded files served inline in FileField and ImageField

## Summary
Severity: High
Advisory: GHSA-8559-gwj3-q37r
CVE: CVE-2026-54087
CWE: CWE-434, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-8559-gwj3-q37r
Type: github-advisory

## Affected
- Packagist: `easycorp/easyadmin-bundle` — affected >=5.0.0 <5.0.13

## Details
EasyAdmin's `FileField` and `ImageField` accept browser-executable file types by default (`FileField` applies no MIME/extension restrictions; `ImageField`'s default `Image` constraint accepts SVG). When the upload directory is configured inside the public web root — as shown in the documentation — EasyAdmin links to the stored file inline (no download attribute or `Content-Disposition: attachment`).

An attacker with access to a form using these fields can upload an `.html` (`FileField`) or `.svg` (`ImageField`) file containing JavaScript. When another  user opens it from the backend, it is served from the same origin and the script executes in the context of their authenticated admin session, enabling session/CSRF-token theft or privilege escalation.

Exploitation requires the developer to store uploads in the public directory and a privilege gap between the uploading user and the viewing administrator. This is stored XSS only — it does not allow remote code execution, because uploaded filenames are derived from Symfony's `guessExtension()`, which never produces `.php`/`.phtml`.

Credit

We would like to thank Emre Dogan for reporting the issue.

## References
- https://github.com/EasyCorp/EasyAdminBundle/security/advisories/GHSA-8559-gwj3-q37r
- https://github.com/EasyCorp/EasyAdminBundle/commit/8132b2b0ca3876c9261264fa267106a1b2c10a68
- https://github.com/EasyCorp/EasyAdminBundle
- https://github.com/EasyCorp/EasyAdminBundle/releases/tag/v5.0.13
