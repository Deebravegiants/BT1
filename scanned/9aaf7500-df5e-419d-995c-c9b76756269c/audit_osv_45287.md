# [H] An out-of-memory flaw was found in libtiff that could be triggered by passing a crafted tiff file to...

## Summary
Severity: High
Advisory: JLSEC-2025-315
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-315
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.6.0+0

## Details
An out-of-memory flaw was found in libtiff that could be triggered by passing a crafted tiff file to the TIFFRasterScanlineSize64() API. This flaw allows a remote attacker to cause a denial of service via a crafted input with a size smaller than 379 KB.

## References
- https://access.redhat.com/errata/RHSA-2025:20801
- https://access.redhat.com/errata/RHSA-2025:21994
- https://access.redhat.com/errata/RHSA-2025:23078
- https://access.redhat.com/errata/RHSA-2025:23079
- https://access.redhat.com/errata/RHSA-2025:23080
- https://access.redhat.com/errata/RHSA-2026:3461
- https://access.redhat.com/errata/RHSA-2026:3462
- https://access.redhat.com/security/cve/CVE-2023-52355
- https://bugzilla.redhat.com/show_bug.cgi?id=2251326
- https://gitlab.com/libtiff/libtiff/-/issues/621
