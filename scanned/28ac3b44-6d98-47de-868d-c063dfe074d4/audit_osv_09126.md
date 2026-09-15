# [M] CVE-2016-8318

## Summary
Severity: Medium
Advisory: CVE-2016-8318
CVSS: 6.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:N/A:H)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/CVE-2016-8318
Type: osv

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: Security: Encryption). Supported versions that are affected are 5.6.34 and earlier and 5.7.16 and earlier. Easily exploitable vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks require human interaction from a person other than the attacker and while the vulnerability is in MySQL Server, attacks may significantly impact additional products. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS v3.0 Base Score 6.8 (Availability impacts).

## References
- http://www.securityfocus.com/bid/95580
- http://www.securitytracker.com/id/1037640
- https://security.gentoo.org/glsa/201702-17
- http://www.oracle.com/technetwork/security-advisory/cpujan2017-2881727.html
