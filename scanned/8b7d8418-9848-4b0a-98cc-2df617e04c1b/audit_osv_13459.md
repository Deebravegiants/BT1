# [H] CVE-2018-1999001

## Summary
Severity: High
Advisory: CVE-2018-1999001
Aliases: GHSA-j8qv-mj4r-6fw4
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-1999001
Type: osv

## Details
A unauthorized modification of configuration vulnerability exists in Jenkins 2.132 and earlier, 2.121.1 and earlier in User.java that allows attackers to provide crafted login credentials that cause Jenkins to move the config.xml file from the Jenkins home directory. If Jenkins is started without this file present, it will revert to the legacy defaults of granting administrator access to anonymous users.

## References
- https://jenkins.io/security/advisory/2018-07-18/#SECURITY-897
- https://www.oracle.com/security-alerts/cpuapr2022.html
