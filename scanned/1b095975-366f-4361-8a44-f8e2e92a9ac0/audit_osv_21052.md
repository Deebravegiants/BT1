# [H] CVE-2021-40145

## Summary
Severity: High
Advisory: CVE-2021-40145
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-26
Source: https://osv.dev/vulnerability/CVE-2021-40145
Type: osv

## Details
gdImageGd2Ptr in gd_gd2.c in the GD Graphics Library (aka LibGD) through 2.3.2 has a double free. NOTE: the vendor's position is "The GD2 image format is a proprietary image format of libgd. It has to be regarded as being obsolete, and should only be used for development and testing purposes.

## References
- https://github.com/libgd/libgd/issues/700
- https://github.com/libgd/libgd/pull/713
- https://github.com/libgd/libgd/commit/c5fd25ce0e48fd5618a972ca9f5e28d6d62006af
