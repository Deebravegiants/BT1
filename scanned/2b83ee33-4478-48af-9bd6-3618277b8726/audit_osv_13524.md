# [M] CVE-2018-20170

## Summary
Severity: Medium
Advisory: CVE-2018-20170
Aliases: PYSEC-2018-9
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-12-17
Source: https://osv.dev/vulnerability/CVE-2018-20170
Type: osv

## Details
OpenStack Keystone through 14.0.1 has a user enumeration vulnerability because invalid usernames have much faster responses than valid ones for a POST /v3/auth/tokens request. NOTE: the vendor's position is that this is a hardening opportunity, and not necessarily an issue that should have an OpenStack Security Advisory

## References
- https://bugs.launchpad.net/keystone/+bug/1795800
