# [H] CVE-2021-23259

## Summary
Severity: High
Advisory: CVE-2021-23259
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-02
Source: https://osv.dev/vulnerability/CVE-2021-23259
Type: osv

## Details
Authenticated users with Administrator or Developer roles may execute OS commands by Groovy Script which uses Groovy lib to render a webpage. The groovy script does not have security restrictions, which will cause attackers to execute arbitrary commands remotely(RCE).

## References
- https://docs.craftercms.org/en/3.1/security/advisory.html#cv-2021120102
