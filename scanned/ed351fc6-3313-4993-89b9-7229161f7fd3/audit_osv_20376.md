# [C] CVE-2021-33357

## Summary
Severity: Critical
Advisory: CVE-2021-33357
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-09
Source: https://osv.dev/vulnerability/CVE-2021-33357
Type: osv

## Details
A vulnerability exists in RaspAP 2.6 to 2.6.5 in the "iface" GET parameter in /ajax/networking/get_netcfg.php, when the "iface" parameter value contains special characters such as ";" which enables an unauthenticated attacker to execute arbitrary OS commands.

## References
- https://gist.github.com/omriinbar/52c000c02a6992c6ce68d531195f69cf
- https://github.com/RaspAP/raspap-webgui/blob/master/ajax/networking/get_netcfg.php
