# [M] CVE-2018-19826

## Summary
Severity: Medium
Advisory: CVE-2018-19826
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-03
Source: https://osv.dev/vulnerability/CVE-2018-19826
Type: osv

## Details
In inspect.cpp in LibSass 3.5.5, a high memory footprint caused by an endless loop (containing a Sass::Inspect::operator()(Sass::String_Quoted*) stack frame) may cause a Denial of Service via crafted sass input files with stray '&' or '/' characters. NOTE: Upstream comments indicate this issue is closed as "won't fix" and "works as intended" by design

## References
- https://github.com/sass/libsass/issues/2781
