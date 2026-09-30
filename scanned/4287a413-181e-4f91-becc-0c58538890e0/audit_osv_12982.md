# [M] CVE-2018-16703

## Summary
Severity: Medium
Advisory: CVE-2018-16703
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-09-07
Source: https://osv.dev/vulnerability/CVE-2018-16703
Type: osv

## Details
A vulnerability in the Gleez CMS 1.2.0 login page could allow an unauthenticated, remote attacker to perform multiple user enumerations, which can further help an attacker to perform login attempts in excess of the configured login attempt limit. The vulnerability is due to insufficient server-side access control and login attempt limit enforcement. An attacker could exploit this vulnerability by sending modified login attempts to the Portal login page. An exploit could allow the attacker to identify existing users and perform brute-force password attacks on the Portal, as demonstrated by navigating to the user/4 URI.

## References
- https://github.com/gleez/cms/issues/802
