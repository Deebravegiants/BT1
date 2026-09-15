# [H] CVE-2021-25630

## Summary
Severity: High
Advisory: CVE-2021-25630
Aliases: GHSA-49w3-gr3w-m68v
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-23
Source: https://osv.dev/vulnerability/CVE-2021-25630
Type: osv

## Details
"loolforkit" is a privileged program that is supposed to be run by a special, non-privileged "lool" user. Before doing anything else "loolforkit" checks, if it was invoked by the "lool" user, and refuses to run with privileges, if it's not the case. In the vulnerable version of "loolforkit" this check was wrong, so a normal user could start "loolforkit" and eventually get local root privileges.

## References
- https://github.com/CollaboraOnline/online/security/advisories/GHSA-49w3-gr3w-m68v
- https://www.openwall.com/lists/oss-security/2021/01/18/3
