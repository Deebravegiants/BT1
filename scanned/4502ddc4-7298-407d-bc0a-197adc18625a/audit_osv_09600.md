# [H] CVE-2017-1000356

## Summary
Severity: High
Advisory: CVE-2017-1000356
Aliases: GHSA-85wq-pqhp-hmq6
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-29
Source: https://osv.dev/vulnerability/CVE-2017-1000356
Type: osv

## Details
Jenkins versions 2.56 and earlier as well as 2.46.1 LTS and earlier are vulnerable to an issue in the Jenkins user database authentication realm: create an account if signup is enabled; or create an account if the victim is an administrator, possibly deleting the existing default admin user in the process and allowing a wide variety of impacts.

## References
- http://www.securityfocus.com/bid/98062
- https://jenkins.io/security/advisory/2017-04-26/
