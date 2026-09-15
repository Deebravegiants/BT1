# [C] CVE-2021-29922

## Summary
Severity: Critical
Advisory: CVE-2021-29922
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2021-08-07
Source: https://osv.dev/vulnerability/CVE-2021-29922
Type: osv

## Details
library/std/src/net/parser.rs in Rust before 1.53.0 does not properly consider extraneous zero characters at the beginning of an IP address string, which (in some situations) allows attackers to bypass access control that is based on IP addresses, because of unexpected octal interpretation.

## References
- https://defcon.org/html/defcon-29/dc-29-speakers.html#kaoudis
- https://doc.rust-lang.org/beta/std/net/struct.Ipv4Addr.html
- https://security.gentoo.org/glsa/202210-09
- https://github.com/rust-lang/rust/issues/83648
- https://github.com/rust-lang/rust/pull/83652
- https://github.com/sickcodes/security/blob/master/advisories/SICK-2021-015.md
