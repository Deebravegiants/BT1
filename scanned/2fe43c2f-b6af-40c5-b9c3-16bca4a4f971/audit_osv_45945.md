# [M] JLSEC-2026-503

## Summary
Severity: Medium
Advisory: JLSEC-2026-503
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-18
Source: https://osv.dev/vulnerability/JLSEC-2026-503
Type: osv

## Affected
- Julia: `libsass_jll` — affected >=0 <3.6.4+0

## Details
In LibSass 3.5.5, a NULL Pointer Dereference in the function Sass::Eval::operator()(`Sass::Supports_Operator`*) in eval.cpp may cause a Denial of Service (application crash) via a crafted sass input file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00051.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00027.html
- http://www.securityfocus.com/bid/106232
- https://github.com/sass/libsass/issues/2786
