# [M] CVE-2018-19839

## Summary
Severity: Medium
Advisory: CVE-2018-19839
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-04
Source: https://osv.dev/vulnerability/CVE-2018-19839
Type: osv

## Details
In LibSass prior to 3.5.5, the function handle_error in sass_context.cpp allows attackers to cause a denial-of-service resulting from a heap-based buffer over-read via a crafted sass file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00051.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00027.html
- https://github.com/sass/libsass/pull/2767
- https://github.com/sass/libsass/issues/2657
