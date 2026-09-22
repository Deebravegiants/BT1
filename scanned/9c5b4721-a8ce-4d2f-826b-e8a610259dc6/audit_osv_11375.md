# [M] CVE-2017-7585

## Summary
Severity: Medium
Advisory: CVE-2017-7585
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-07
Source: https://osv.dev/vulnerability/CVE-2017-7585
Type: osv

## Details
In libsndfile before 1.0.28, an error in the "flac_buffer_copy()" function (flac.c) can be exploited to cause a stack-based buffer overflow via a specially crafted FLAC file.

## References
- http://www.mega-nerd.com/libsndfile/#History
- http://www.mega-nerd.com/libsndfile/NEWS
- https://secuniaresearch.flexerasoftware.com/secunia_research/2017-4/
- https://security.gentoo.org/glsa/201707-04
- https://github.com/erikd/libsndfile/commit/60b234301adf258786d8b90be5c1d437fc8799e0
