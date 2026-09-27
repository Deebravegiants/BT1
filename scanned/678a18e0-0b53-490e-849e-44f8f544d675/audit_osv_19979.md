# [H] CVE-2021-28877

## Summary
Severity: High
Advisory: CVE-2021-28877
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-11
Source: https://osv.dev/vulnerability/CVE-2021-28877
Type: osv

## Details
In the standard library in Rust before 1.51.0, the Zip implementation calls __iterator_get_unchecked() for the same index more than once when nested. This bug can lead to a memory safety violation due to an unmet safety requirement for the TrustedRandomAccess trait.

## References
- https://security.gentoo.org/glsa/202210-09
- https://github.com/rust-lang/rust/pull/80670
