# [H] CVE-2020-24848

## Summary
Severity: High
Advisory: CVE-2020-24848
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-23
Source: https://osv.dev/vulnerability/CVE-2020-24848
Type: osv

## Details
FruityWifi through 2.4 has an unsafe Sudo configuration [(ALL : ALL) NOPASSWD: ALL]. This allows an attacker to perform a system-level (root) local privilege escalation, allowing an attacker to gain complete persistent access to the local system.

## References
- https://gist.github.com/harsh-bothra/5be73cfd53f1c5bea307c702ae83ff42
- https://github.com/xtr4nge/FruityWifi/issues/278
