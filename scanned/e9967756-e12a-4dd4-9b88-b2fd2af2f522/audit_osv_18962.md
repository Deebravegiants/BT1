# [H] CVE-2020-5281

## Summary
Severity: High
Advisory: CVE-2020-5281
Aliases: GHSA-gj88-9q3f-72m3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-03-25
Source: https://osv.dev/vulnerability/CVE-2020-5281
Type: osv

## Details
In Perun before version 3.9.1, VO or group manager can modify configuration of the LDAP extSource to retrieve all from Perun LDAP. Issue is fixed in version 3.9.1 by sanitisation of the input.

## References
- https://github.com/CESNET/perun/security/advisories/GHSA-gj88-9q3f-72m3
- https://github.com/CESNET/perun/commit/ac527bc3225a64208ee5cee59e5918ee360ca039
- https://github.com/CESNET/perun/pull/2635
