# [M] CVE-2018-14047

## Summary
Severity: Medium
Advisory: CVE-2018-14047
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-13
Source: https://osv.dev/vulnerability/CVE-2018-14047
Type: osv

## Details
An issue has been found in PNGwriter 0.7.0. It is a SEGV in pngwriter::readfromfile in pngwriter.cc. NOTE: there is a "Warning: PNGwriter was never designed for reading untrusted files with it. Do NOT use this in sensitive environments, especially DO NOT read PNGs from unknown sources with it!" statement in the master/README.md file

## References
- https://github.com/fouzhe/security/tree/master/pngwriter
- https://github.com/pngwriter/pngwriter/issues/129
