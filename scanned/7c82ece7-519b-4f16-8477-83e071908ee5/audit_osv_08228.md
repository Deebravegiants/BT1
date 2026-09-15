# [H] CVE-2016-1587

## Summary
Severity: High
Advisory: CVE-2016-1587
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-22
Source: https://osv.dev/vulnerability/CVE-2016-1587
Type: osv

## Details
The Snapweb interface before version 0.21.2 was exposing controls to install or remove snap packages without controlling the identity of the user, nor the origin of the connection. An attacker could have used the controls to remotely add a valid, but malicious, snap package, from the Store, potentially using system resources without permission from the legitimate administrator of the system.

## References
- https://github.com/snapcore/snapweb/commit/3f4cf9403f7687fbc8e27c0e01b2cf6aa5e7e0d5
