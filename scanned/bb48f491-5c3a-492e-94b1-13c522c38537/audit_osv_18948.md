# [C] CVE-2020-5253

## Summary
Severity: Critical
Advisory: CVE-2020-5253
Aliases: GHSA-2c7p-3fj4-223m
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-10
Source: https://osv.dev/vulnerability/CVE-2020-5253
Type: osv

## Details
NetHack before version 3.6.0 allowed malicious use of escaping of characters in the configuration file (usually .nethackrc) which could be exploited. This bug is patched in NetHack 3.6.0.

## References
- https://github.com/NetHack/NetHack/security/advisories/GHSA-2c7p-3fj4-223m
- https://github.com/NetHack/NetHack/commits/612755bfb5c412079795c68ba392df5d93874ed8
