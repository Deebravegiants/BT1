# [H] CVE-2019-6468

## Summary
Severity: High
Advisory: CVE-2019-6468
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-09
Source: https://osv.dev/vulnerability/CVE-2019-6468
Type: osv

## Details
In BIND Supported Preview Edition, an error in the nxdomain-redirect feature can occur in versions which support EDNS Client Subnet (ECS) features. In those versions which have ECS support, enabling nxdomain-redirect is likely to lead to BIND exiting due to assertion failure. Versions affected: BIND Supported Preview Edition version 9.10.5-S1 -> 9.11.5-S5. ONLY BIND Supported Preview Edition releases are affected.

## References
- https://kb.isc.org/docs/cve-2019-6468
- https://www.synology.com/security/advisory/Synology_SA_19_20
