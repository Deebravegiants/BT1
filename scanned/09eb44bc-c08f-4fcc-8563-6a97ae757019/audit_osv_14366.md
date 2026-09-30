# [H] CVE-2018-9841

## Summary
Severity: High
Advisory: CVE-2018-9841
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-07
Source: https://osv.dev/vulnerability/CVE-2018-9841
Type: osv

## Details
The export function in libavfilter/vf_signature.c in FFmpeg through 3.4.2 allows remote attackers to cause a denial of service (out-of-array access) or possibly have unspecified other impact via a long filename.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commit%3Bh=35eeff30caf34df835206f1c12bcf4b7c2bd6758
- https://security.gentoo.org/glsa/202003-65
