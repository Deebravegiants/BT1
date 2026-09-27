# [M] CVE-2017-11552

## Summary
Severity: Medium
Advisory: CVE-2017-11552
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-01
Source: https://osv.dev/vulnerability/CVE-2017-11552
Type: osv

## Details
mpg321.c in mpg321 0.3.2-1 does not properly manage memory for use with libmad 0.15.1b, which allows remote attackers to cause a denial of service (memory corruption seen in a crash in the mad_decoder_run function in decoder.c in libmad) via a crafted MP3 file.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=870406
- https://www.exploit-db.com/exploits/42409/
- http://seclists.org/fulldisclosure/2017/Jul/94
