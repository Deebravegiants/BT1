# [M] CVE-2017-6966

## Summary
Severity: Medium
Advisory: CVE-2017-6966
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-17
Source: https://osv.dev/vulnerability/CVE-2017-6966
Type: osv

## Details
readelf in GNU Binutils 2.28 has a use-after-free (specifically read-after-free) error while processing multiple, relocated sections in an MSP430 binary. This is caused by mishandling of an invalid symbol index, and mishandling of state across invocations.

## References
- https://security.gentoo.org/glsa/201709-02
- https://sourceware.org/bugzilla/show_bug.cgi?id=21139
