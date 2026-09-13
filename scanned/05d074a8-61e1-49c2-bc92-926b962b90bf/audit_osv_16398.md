# [H] CVE-2019-6467

## Summary
Severity: High
Advisory: CVE-2019-6467
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-09
Source: https://osv.dev/vulnerability/CVE-2019-6467
Type: osv

## Details
A programming error in the nxdomain-redirect feature can cause an assertion failure in query.c if the alternate namespace used by nxdomain-redirect is a descendant of a zone that is served locally. The most likely scenario where this might occur is if the server, in addition to performing NXDOMAIN redirection for recursive clients, is also serving a local copy of the root zone or using mirroring to provide the root zone, although other configurations are also possible. Versions affected: BIND 9.12.0-> 9.12.4, 9.14.0. Also affects all releases in the 9.13 development branch.

## References
- https://kb.isc.org/docs/cve-2019-6467
- https://www.synology.com/security/advisory/Synology_SA_19_20
