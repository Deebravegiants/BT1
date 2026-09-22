# [M] A segmentation fault (SEGV) flaw was found in the Fribidi package and affects the...

## Summary
Severity: Medium
Advisory: JLSEC-2025-172
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-20
Source: https://osv.dev/vulnerability/JLSEC-2025-172
Type: osv

## Affected
- Julia: `FriBidi_jll` — affected >=0 <1.0.14+0

## Details
A segmentation fault (SEGV) flaw was found in the Fribidi package and affects the `fribidi_remove_bidi_marks()` function of the `lib/fribidi.c` file. This flaw allows an attacker to pass a specially crafted file to Fribidi, leading to a crash and causing a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2022-25310
- https://bugzilla.redhat.com/show_bug.cgi?id=2047923
- https://github.com/fribidi/fribidi/issues/183
- https://github.com/fribidi/fribidi/pull/186
