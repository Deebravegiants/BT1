# [M] CVE-2020-5246

## Summary
Severity: Medium
Advisory: CVE-2020-5246
Aliases: GHSA-v955-7g22-2p49
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-07-14
Source: https://osv.dev/vulnerability/CVE-2020-5246
Type: osv

## Details
Traccar GPS Tracking System before version 4.9 has a LDAP injection vulnerability. It occurs when user input is being used in LDAP search filter. By providing specially crafted input, an attacker can modify the logic of the LDAP query and get admin privileges. The issue only impacts instances with LDAP configuration and where users can craft their own names. This has been patched in version 4.9.

## References
- https://github.com/traccar/traccar/security/advisories/GHSA-v955-7g22-2p49
- https://github.com/traccar/traccar/commit/e4f6e74e57ab743b65d49ae00f6624a20ca0291e
