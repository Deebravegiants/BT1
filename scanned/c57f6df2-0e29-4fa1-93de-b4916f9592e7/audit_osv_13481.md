# [H] CVE-2018-1999043

## Summary
Severity: High
Advisory: CVE-2018-1999043
Aliases: GHSA-2632-h32j-6rg9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-23
Source: https://osv.dev/vulnerability/CVE-2018-1999043
Type: osv

## Details
A denial of service vulnerability exists in Jenkins 2.137 and earlier, 2.121.2 and earlier in BasicAuthenticationFilter.java, BasicHeaderApiTokenAuthenticator.java that allows attackers to create ephemeral in-memory user records by attempting to log in using invalid credentials.

## References
- https://jenkins.io/security/advisory/2018-08-15/#SECURITY-672
