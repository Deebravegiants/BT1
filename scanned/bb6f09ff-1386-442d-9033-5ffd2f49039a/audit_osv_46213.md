# [H] JLSEC-2026-822

## Summary
Severity: High
Advisory: JLSEC-2026-822
Ecosystem: Julia
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-822
Type: osv

## Affected
- Julia: `Giflib_jll` — affected >=5.2.2+0 <6.1.3+0

## Details
Buffer Overflow vulnerability in giflib v.5.2.2 allows a remote attacker to cause a denial of service via the EGifGCBToExtension overwriting an existing Graphic Control Extension block without validating its allocated size.

## References
- https://access.redhat.com/errata/RHSA-2026:33447
- https://access.redhat.com/errata/RHSA-2026:33450
- https://access.redhat.com/errata/RHSA-2026:33451
- https://access.redhat.com/errata/RHSA-2026:33452
- https://access.redhat.com/errata/RHSA-2026:33455
- https://access.redhat.com/errata/RHSA-2026:33456
- https://access.redhat.com/errata/RHSA-2026:33501
- https://access.redhat.com/errata/RHSA-2026:33502
- https://access.redhat.com/errata/RHSA-2026:33503
- https://access.redhat.com/errata/RHSA-2026:33509
- https://access.redhat.com/errata/RHSA-2026:36004
- https://access.redhat.com/errata/RHSA-2026:36005
- https://access.redhat.com/errata/RHSA-2026:36006
- https://access.redhat.com/errata/RHSA-2026:9683
- https://access.redhat.com/errata/RHSA-2026:9686
- https://access.redhat.com/errata/RHSA-2026:9689
- https://access.redhat.com/errata/RHSA-2026:9693
- https://access.redhat.com/security/cve/CVE-2026-26740
- https://bugzilla.redhat.com/show_bug.cgi?id=2448747
- https://github.com/zakkanijia/POC/blob/main/giflib/giftool/giflib_giftool_gce_len_heap_oobwrite_disclosure.md
