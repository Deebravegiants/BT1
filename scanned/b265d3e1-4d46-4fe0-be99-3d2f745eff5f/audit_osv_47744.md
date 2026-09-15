# [M] CVE-2017-11331

## Summary
Severity: Medium
Advisory: CVE-2017-11331
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-31
Source: https://osv.dev/vulnerability/CVE-2017-11331
Type: osv

## Details
The wav_open function in oggenc/audio.c in Xiph.Org vorbis-tools 1.4.0 allows remote attackers to cause a denial of service (memory allocation error) via a crafted wav file.

## References
- http://seclists.org/fulldisclosure/2017/Jul/80
- https://www.exploit-db.com/exploits/42397/
