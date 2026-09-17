# [H] CVE-2018-6353

## Summary
Severity: High
Advisory: CVE-2018-6353
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-27
Source: https://osv.dev/vulnerability/CVE-2018-6353
Type: osv

## Details
The Python console in Electrum through 2.9.4 and 3.x through 3.0.5 supports arbitrary Python code without considering (1) social-engineering attacks in which a user pastes code that they do not understand and (2) code pasted by a physically proximate attacker at an unattended workstation, which makes it easier for attackers to steal Bitcoin via hook code that runs at a later time when the wallet password has been entered, a different vulnerability than CVE-2018-1000022.

## References
- https://github.com/spesmilo/electrum/pull/3700
- https://github.com/spesmilo/electrum/issues/3678
