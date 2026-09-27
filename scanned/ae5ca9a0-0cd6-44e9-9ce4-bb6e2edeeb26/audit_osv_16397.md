# [M] CVE-2019-6465

## Summary
Severity: Medium
Advisory: CVE-2019-6465
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-10-09
Source: https://osv.dev/vulnerability/CVE-2019-6465
Type: osv

## Details
Controls for zone transfers may not be properly applied to Dynamically Loadable Zones (DLZs) if the zones are writable Versions affected: BIND 9.9.0 -> 9.10.8-P1, 9.11.0 -> 9.11.5-P2, 9.12.0 -> 9.12.3-P2, and versions 9.9.3-S1 -> 9.11.5-S3 of BIND 9 Supported Preview Edition. Versions 9.13.0 -> 9.13.6 of the 9.13 development branch are also affected. Versions prior to BIND 9.9.0 have not been evaluated for vulnerability to CVE-2019-6465.

## References
- https://access.redhat.com/errata/RHSA-2019:3552
- https://kb.isc.org/docs/cve-2019-6465
