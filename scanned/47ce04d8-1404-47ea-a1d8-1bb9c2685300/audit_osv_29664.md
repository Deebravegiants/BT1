# [M] Disabled user can bypass lockout by requesting password reset in wiki.js

## Summary
Severity: Medium
Advisory: CVE-2024-45298
Aliases: GHSA-vwww-c5vg-xgfc
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-45298
Type: osv

## Details
Wiki.js is an open source wiki app built on Node.js. A disabled user can still gain access to a wiki by abusing the password reset function. While setting up SMTP e-mail's on my server, I tested said e-mails by performing a password reset with my test user. To my shock, not only did it let me reset my password, but after resetting my password I can get into the wiki I was locked out of. The ramifications of this bug is a user can **bypass an account disabling by requesting their password be reset**.  All users of wiki.js version `2.5.303` who use any account restrictions and have disabled user are affected. This issue has been addressed in version 2.5.304 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45298.json
- https://github.com/requarks/wiki/security/advisories/GHSA-vwww-c5vg-xgfc
- https://nvd.nist.gov/vuln/detail/CVE-2024-45298
- https://github.com/requarks/wiki/commit/b9fb17d4d4a0956ec35e8c73cc85192552fb8d16
