# [M] CVE-2017-15185

## Summary
Severity: Medium
Advisory: CVE-2017-15185
CVSS: 5.0 (CVSS:3.0/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-09
Source: https://osv.dev/vulnerability/CVE-2017-15185
Type: osv

## Details
plugins/ogg.c in Libmp3splt 0.9.2 calls the libvorbis vorbis_block_clear function with uninitialized data upon detection of invalid input, which allows remote attackers to cause a denial of service (application crash) via a crafted file.

## References
- http://seclists.org/fulldisclosure/2017/Jul/82
- https://anonscm.debian.org/cgit/users/ron/mp3splt.git/commit/?id=18f018cd774cb931116ce06a520dc0c5f9443932
- https://lists.debian.org/debian-lts/2017/09/msg00115.html
- https://www.exploit-db.com/exploits/42399/
