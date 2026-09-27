# [C] Strapi allows unauthenticated attacker to reset admin password without valid reset token

## Summary
Severity: Critical
Advisory: GHSA-6xc2-mj39-q599
CVE: CVE-2019-18818
CWE: CWE-640
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-12-02
Source: https://github.com/advisories/GHSA-6xc2-mj39-q599
Type: github-advisory

## Affected
- npm: `strapi` — affected >=0 <3.0.0-beta.17.5

## Details
Versions of `strapi` prior to 3.0.0-beta.17.5 are vulnerable to Privilege Escalation. The password reset routes allows an unauthenticated attacker to reset an admin's password without providing a valid password reset token.


## Recommendation

Upgrade to version 3.0.0-beta.17.5 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18818
- https://github.com/strapi/strapi/pull/4443
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-18818
- https://github.com/strapi/strapi
- https://github.com/strapi/strapi/releases/tag/v3.0.0-beta.17.5
- https://www.npmjs.com/advisories/1311
- http://packetstormsecurity.com/files/163939/Strapi-3.0.0-beta-Authentication-Bypass.html
- http://packetstormsecurity.com/files/163950/Strapi-CMS-3.0.0-beta.17.4-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/165896/Strapi-CMS-3.0.0-beta.17.4-Privilege-Escalation.html
