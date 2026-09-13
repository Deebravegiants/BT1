# [M] CVE-2017-11333

## Summary
Severity: Medium
Advisory: CVE-2017-11333
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-31
Source: https://osv.dev/vulnerability/CVE-2017-11333
Type: osv

## Details
The vorbis_analysis_wrote function in lib/block.c in Xiph.Org libvorbis 1.3.5 allows remote attackers to cause a denial of service (OOM) via a crafted wav file.

## References
- https://lists.debian.org/debian-lts-announce/2018/04/msg00033.html
- https://lists.debian.org/debian-lts-announce/2019/12/msg00021.html
- https://www.exploit-db.com/exploits/42399/
- http://seclists.org/fulldisclosure/2017/Jul/82
