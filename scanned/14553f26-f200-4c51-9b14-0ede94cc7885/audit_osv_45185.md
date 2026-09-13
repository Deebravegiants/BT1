# [H] A stack-based buffer overflow flaw was found in the Fribidi package

## Summary
Severity: High
Advisory: JLSEC-2025-170
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-20
Source: https://osv.dev/vulnerability/JLSEC-2025-170
Type: osv

## Affected
- Julia: `FriBidi_jll` — affected >=0 <1.0.14+0

## Details
A stack-based buffer overflow flaw was found in the Fribidi package. This flaw allows an attacker to pass a specially crafted file to the Fribidi application, which leads to a possible memory leak or a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2022-25308
- https://bugzilla.redhat.com/show_bug.cgi?id=2047890
- https://github.com/fribidi/fribidi/issues/181
- https://github.com/fribidi/fribidi/pull/184
