# [M] CVE-2017-11359

## Summary
Severity: Medium
Advisory: CVE-2017-11359
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-31
Source: https://osv.dev/vulnerability/CVE-2017-11359
Type: osv

## Details
The wavwritehdr function in wav.c in Sound eXchange (SoX) 14.4.2 allows remote attackers to cause a denial of service (divide-by-zero error and application crash) via a crafted snd file, during conversion to a wav file.

## References
- https://lists.debian.org/debian-lts-announce/2017/11/msg00043.html
- https://lists.debian.org/debian-lts-announce/2019/03/msg00007.html
- https://security.gentoo.org/glsa/201810-02
- http://seclists.org/fulldisclosure/2017/Jul/81
- https://www.exploit-db.com/exploits/42398/
