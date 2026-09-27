# [M] JLSEC-2026-821

## Summary
Severity: Medium
Advisory: JLSEC-2026-821
Ecosystem: Julia
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-821
Type: osv

## Affected
- Julia: `Giflib_jll` — affected >=0 <6.1.3+0

## Details
Giflib contains a double-free vulnerability that is the result of a shallow copy in GifMakeSavedImage and incorrect error handling. The conditions needed to trigger this vulnerability are difficult but may be possible.

## References
- https://access.redhat.com/errata/RHSA-2026:16008
- https://access.redhat.com/errata/RHSA-2026:16009
- https://access.redhat.com/errata/RHSA-2026:16030
- https://access.redhat.com/errata/RHSA-2026:16174
- https://access.redhat.com/errata/RHSA-2026:19154
- https://access.redhat.com/errata/RHSA-2026:19367
- https://access.redhat.com/errata/RHSA-2026:19724
- https://access.redhat.com/errata/RHSA-2026:19725
- https://access.redhat.com/errata/RHSA-2026:25096
- https://access.redhat.com/errata/RHSA-2026:8858
- https://access.redhat.com/errata/RHSA-2026:8859
- https://access.redhat.com/errata/RHSA-2026:8861
- https://access.redhat.com/errata/RHSA-2026:8883
- https://access.redhat.com/errata/RHSA-2026:8884
- https://access.redhat.com/errata/RHSA-2026:8885
- https://access.redhat.com/errata/RHSA-2026:8886
- https://access.redhat.com/errata/RHSA-2026:8887
- https://access.redhat.com/errata/RHSA-2026:9290
- https://access.redhat.com/errata/RHSA-2026:9291
- https://access.redhat.com/errata/RHSA-2026:9292
