# [H] CVE-2018-1000050

## Summary
Severity: High
Advisory: CVE-2018-1000050
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/CVE-2018-1000050
Type: osv

## Details
Sean Barrett stb_vorbis version 1.12 and earlier contains a Buffer Overflow vulnerability in All vorbis decoding paths. that can result in memory corruption, denial of service, comprised execution of host program. This attack appear to be exploitable via Victim must open a specially crafted Ogg Vorbis file. This vulnerability appears to have been fixed in 1.13.

## References
- https://github.com/nothings/stb/commit/244d83bc3d859293f55812d48b3db168e581f6ab
