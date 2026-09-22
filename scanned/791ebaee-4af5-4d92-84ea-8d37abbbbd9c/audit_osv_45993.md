# [M] JLSEC-2026-550

## Summary
Severity: Medium
Advisory: JLSEC-2026-550
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-550
Type: osv

## Affected
- Julia: `OpenJpeg_jll` — affected >=2.5.0+0 <2.5.2+0

## Details
A flaw was found in OpenJPEG. A resource exhaustion can occur in the `opj_t1_decode_cblks` function in tcd.c through a crafted image file, causing a denial of service.

## References
- https://access.redhat.com/errata/RHSA-2026:4128
- https://access.redhat.com/security/cve/CVE-2023-39329
- https://bugzilla.redhat.com/show_bug.cgi?id=2295816
