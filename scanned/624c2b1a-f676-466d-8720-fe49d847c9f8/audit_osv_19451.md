# [H] CVE-2021-21327

## Summary
Severity: High
Advisory: CVE-2021-21327
Aliases: GHSA-qmw7-w2m4-rjwp
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-03-08
Source: https://osv.dev/vulnerability/CVE-2021-21327
Type: osv

## Details
GLPI is an open-source asset and IT management software package that provides ITIL Service Desk features, licenses tracking and software auditing. In GLPI before version 9.5.4 non-authenticated user can remotely instantiate object of any class existing in the GLPI environment that can be used to carry out malicious attacks, or to start a “POP chain”. As an example of direct impact, this vulnerability affects integrity of the GLPI core platform and third-party plugins runtime misusing classes which implement some sensitive operations in their constructors or destructors. This is fixed in version 9.5.4.

## References
- https://github.com/glpi-project/glpi/releases/tag/9.5.4
- https://github.com/glpi-project/glpi/security/advisories/GHSA-qmw7-w2m4-rjwp
- http://packetstormsecurity.com/files/161680/GLPI-9.5.3-Unsafe-Reflection.html
