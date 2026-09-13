# [H] CVE-2018-1000223

## Summary
Severity: High
Advisory: CVE-2018-1000223
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2018-1000223
Type: osv

## Details
soundtouch version up to and including 2.0.0 contains a Buffer Overflow vulnerability in SoundStretch/WavFile.cpp:WavInFile::readHeaderBlock() that can result in arbitrary code execution. This attack appear to be exploitable via victim must open maliocius file in soundstretch utility.

## References
- https://gitlab.com/soundtouch/soundtouch/issues/6
