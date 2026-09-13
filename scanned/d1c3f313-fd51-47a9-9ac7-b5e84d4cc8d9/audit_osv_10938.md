# [C] CVE-2017-5225

## Summary
Severity: Critical
Advisory: CVE-2017-5225
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-12
Source: https://osv.dev/vulnerability/CVE-2017-5225
Type: osv

## Details
LibTIFF version 4.0.7 is vulnerable to a heap buffer overflow in the tools/tiffcp resulting in DoS or code execution via a crafted BitsPerSample value.

## References
- http://www.securitytracker.com/id/1037911
- http://www.debian.org/security/2017/dsa-3844
- http://www.securityfocus.com/bid/95413
- https://security.gentoo.org/glsa/201709-27
- http://bugzilla.maptools.org/show_bug.cgi?id=2656
- http://bugzilla.maptools.org/show_bug.cgi?id=2657
- https://github.com/vadz/libtiff/commit/5c080298d59efa53264d7248bbe3a04660db6ef7
