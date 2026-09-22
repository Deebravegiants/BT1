# [M] CVE-2017-11358

## Summary
Severity: Medium
Advisory: CVE-2017-11358
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-31
Source: https://osv.dev/vulnerability/CVE-2017-11358
Type: osv

## Details
The read_samples function in hcom.c in Sound eXchange (SoX) 14.4.2 allows remote attackers to cause a denial of service (invalid memory read and application crash) via a crafted hcom file.

## References
- http://www.openwall.com/lists/oss-security/2023/02/03/3
- http://www.openwall.com/lists/oss-security/2023/02/04/2
- http://www.openwall.com/lists/oss-security/2023/02/05/1
- http://www.openwall.com/lists/oss-security/2023/02/06/1
- https://security.gentoo.org/glsa/201810-02
- https://lists.debian.org/debian-lts-announce/2017/11/msg00043.html
- https://lists.debian.org/debian-lts-announce/2019/03/msg00007.html
- https://www.exploit-db.com/exploits/42398/
- http://seclists.org/fulldisclosure/2017/Jul/81
