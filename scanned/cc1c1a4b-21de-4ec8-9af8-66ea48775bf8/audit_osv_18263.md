# [M] CVE-2020-25676

## Summary
Severity: Medium
Advisory: CVE-2020-25676
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-08
Source: https://osv.dev/vulnerability/CVE-2020-25676
Type: osv

## Details
In CatromWeights(), MeshInterpolate(), InterpolatePixelChannel(), InterpolatePixelChannels(), and InterpolatePixelInfo(), which are all functions in /MagickCore/pixel.c, there were multiple unconstrained pixel offset calculations which were being used with the floor() function. These calculations produced undefined behavior in the form of out-of-range and integer overflows, as identified by UndefinedBehaviorSanitizer. These instances of undefined behavior could be triggered by an attacker who is able to supply a crafted input file to be processed by ImageMagick. These issues could impact application availability or potentially cause other problems related to undefined behavior. This flaw affects ImageMagick versions prior to 7.0.9-0.

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00030.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1891934
