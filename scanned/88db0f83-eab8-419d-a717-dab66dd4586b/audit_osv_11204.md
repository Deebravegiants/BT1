# [H] CVE-2017-6594

## Summary
Severity: High
Advisory: CVE-2017-6594
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-08-28
Source: https://osv.dev/vulnerability/CVE-2017-6594
Type: osv

## Details
The transit path validation code in Heimdal before 7.3 might allow attackers to bypass the capath policy protection mechanism by leveraging failure to add the previous hop realm to the transit path of issued tickets.

## References
- http://lists.opensuse.org/opensuse-updates/2017-08/msg00062.html
- http://www.h5l.org/advisories.html?show=2017-04-13
- https://github.com/heimdal/heimdal/commit/b1e699103f08d6a0ca46a122193c9da65f6cf837
- https://github.com/heimdal/heimdal/releases/tag/heimdal-7.3.0
