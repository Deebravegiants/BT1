# [H] webbrowser.open() allows leading dashes in URLs

## Summary
Severity: High
Advisory: CVE-2026-4519
Aliases: PSF-2026-14
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-4519
Type: osv

## Details
The webbrowser.open() API would accept leading dashes in the URL which 
could be handled as command line options for certain web browsers. New 
behavior rejects leading dashes. Users are recommended to sanitize URLs 
prior to passing to webbrowser.open().

## References
- http://www.openwall.com/lists/oss-security/2026/03/20/1
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-4519.json
- https://access.redhat.com/errata/RHSA-2026:10065
- https://access.redhat.com/errata/RHSA-2026:10101
- https://access.redhat.com/errata/RHSA-2026:10102
- https://access.redhat.com/errata/RHSA-2026:10111
- https://access.redhat.com/errata/RHSA-2026:10140
- https://access.redhat.com/errata/RHSA-2026:10141
- https://access.redhat.com/errata/RHSA-2026:13812
- https://access.redhat.com/errata/RHSA-2026:16008
- https://access.redhat.com/errata/RHSA-2026:16009
- https://access.redhat.com/errata/RHSA-2026:16030
- https://access.redhat.com/errata/RHSA-2026:16174
- https://access.redhat.com/errata/RHSA-2026:19019
- https://access.redhat.com/errata/RHSA-2026:19064
- https://access.redhat.com/errata/RHSA-2026:19175
- https://access.redhat.com/errata/RHSA-2026:19176
- https://access.redhat.com/errata/RHSA-2026:19177
- https://access.redhat.com/errata/RHSA-2026:19216
- https://access.redhat.com/errata/RHSA-2026:19724
