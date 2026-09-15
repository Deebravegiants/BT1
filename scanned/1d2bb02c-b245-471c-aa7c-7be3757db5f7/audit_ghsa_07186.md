# [M] Decidim: Forms admin question editor lacks authorization

## Summary
Severity: Medium
Advisory: GHSA-vq6j-hj8w-7v39
CVE: CVE-2026-45086
CWE: CWE-284
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-vq6j-hj8w-7v39
Type: github-advisory

## Affected
- RubyGems: `decidim-demographics` — affected >=0.31.0 <0.31.5
- RubyGems: `decidim-demographics` — affected >=0.32.0.rc1 <0.32.0

## Details
## Description

A participant can load the demographics questionnaire admin editor and make changes.

## Technical description

The demographics questionnaire editor should require admin access, but the route under `/admin/demographics/questions` renders the editor interface without checking whether the caller is an admin. A normal participant can load the page and see the live update form action, which proves the protected interface is reachable.

Reproduction steps:

Step 1. Sign in as a normal participant: Open `http://localhost:3000/users/sign_in`.
Step 2. Request the admin-only editor directly. Open `http://localhost:3000/admin/demographics/questions/edit_questions` in the same browser.
Step 3. Add another question:

<img width="1522" height="1174" alt="decidim-questions-01" src="https://github.com/user-attachments/assets/923f85d4-0e2f-4511-a9f3-a92f74dbf1d8" />

Note that access was denied when attempting to see question responses or settings.

### Impact

- Low-privilege users can access questionnaire-admin interfaces.
- They can read question-management surfaces that should remain limited to questionnaire managers.
 
### Patches

See https://github.com/decidim/decidim/pull/16665 

### Workarounds

Disable the "decidim-demographics" module 

### Reference

OWASP A01:2021 Broken Access Control

### Credits

This issue was discovered in a security audit organized by the [Decidim Association](https://decidim.org) and made by [Radically Open Security](https://www.radicallyopensecurity.com/) against Decidim financed by [NGI](https://ngi.eu/).

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-vq6j-hj8w-7v39
- https://github.com/decidim/decidim/pull/16665
- https://github.com/decidim/decidim
