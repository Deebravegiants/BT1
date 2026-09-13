# [H] CVE-2020-27985

## Summary
Severity: High
Advisory: CVE-2020-27985
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-23
Source: https://osv.dev/vulnerability/CVE-2020-27985
Type: osv

## Details
Security Onion v2 prior to 2.3.10 has an incorrect sudo configuration, which allows the administrative user to obtain root access without using the sudo password by editing and executing /home/<user>/SecurityOnion/setup/so-setup.

## References
- https://github.com/Security-Onion-Solutions/securityonion/releases
- https://github.com/Security-Onion-Solutions/securityonion/commit/b14670030349a2747a00ace665568ab5f51ac47b
- https://s1gh.sh/cve-2020-27985-security-onion-local-privilege-escalation/
