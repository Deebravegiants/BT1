# [M] CVE-2017-17446

## Summary
Severity: Medium
Advisory: CVE-2017-17446
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-06
Source: https://osv.dev/vulnerability/CVE-2017-17446
Type: osv

## Details
The Mem_File_Reader::read_avail function in Data_Reader.cpp in the Game_Music_Emu library (aka game-music-emu) 0.6.1 does not ensure a non-negative size, which allows remote attackers to cause a denial of service (application crash) via a crafted file.

## References
- https://bitbucket.org/mpyne/game-music-emu/issues/14/addresssanitizer-negative-size-param-size
- https://bugs.debian.org/883691
