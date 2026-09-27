# [M] JLSEC-2026-549

## Summary
Severity: Medium
Advisory: JLSEC-2026-549
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-549
Type: osv

## Affected
- Julia: `OpenJpeg_jll` — affected >=2.5.0+0 <2.5.2+0

## Details
A vulnerability was found in OpenJPEG similar to CVE-2019-6988. This flaw allows an attacker to bypass existing protections and cause an application crash through a maliciously crafted file.

## References
- https://access.redhat.com/security/cve/CVE-2023-39328
- https://bugzilla.redhat.com/show_bug.cgi?id=2219236
- https://github.com/uclouvain/openjpeg/issues/1476
- https://github.com/uclouvain/openjpeg/pull/1470
- https://github.com/uclouvain/openjpeg/pull/1471
