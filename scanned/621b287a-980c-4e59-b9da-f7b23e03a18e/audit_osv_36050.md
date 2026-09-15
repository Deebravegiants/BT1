# [H] Samba: missing access check on reparse point operations

## Summary
Severity: High
Advisory: CVE-2026-1933
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-1933
Type: osv

## Details
A flaw was found in Samba’s handling of NTFS-style reparse points on shares configured with read only = yes. Due to missing SMB-layer access checks, authenticated users with underlying filesystem write permissions may create or delete reparse point metadata through SMB operations even on read-only exports. This could allow modification of SMB-visible file behavior, including converting files into symbolic links or other reparse point types.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-1933.json
- https://access.redhat.com/errata/RHSA-2026:22644
- https://access.redhat.com/errata/RHSA-2026:22963
- https://access.redhat.com/errata/RHSA-2026:25049
- https://access.redhat.com/errata/RHSA-2026:25979
- https://access.redhat.com/errata/RHSA-2026:28053
- https://access.redhat.com/errata/RHSA-2026:28054
- https://access.redhat.com/errata/RHSA-2026:28055
- https://access.redhat.com/errata/RHSA-2026:28056
- https://access.redhat.com/errata/RHSA-2026:28057
- https://access.redhat.com/errata/RHSA-2026:29863
- https://access.redhat.com/errata/RHSA-2026:54581
- https://access.redhat.com/errata/RHSA-2026:54599
- https://access.redhat.com/errata/RHSA-2026:54769
- https://access.redhat.com/errata/RHSA-2026:56786
- https://access.redhat.com/errata/RHSA-2026:56853
- https://access.redhat.com/errata/RHSA-2026:56911
- https://access.redhat.com/errata/RHSA-2026:57483
- https://access.redhat.com/errata/RHSA-2026:59831
