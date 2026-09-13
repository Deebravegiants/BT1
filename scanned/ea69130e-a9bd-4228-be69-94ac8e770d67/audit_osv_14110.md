# [H] CVE-2018-7254

## Summary
Severity: High
Advisory: CVE-2018-7254
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-19
Source: https://osv.dev/vulnerability/CVE-2018-7254
Type: osv

## Details
The ParseCaffHeaderConfig function of the cli/caff.c file of WavPack 5.1.0 allows a remote attacker to cause a denial-of-service (global buffer over-read), or possibly trigger a buffer overflow or incorrect memory allocation, via a maliciously crafted CAF file.

## References
- http://packetstormsecurity.com/files/155743/Slackware-Security-Advisory-wavpack-Updates.html
- https://seclists.org/bugtraq/2019/Dec/37
- https://usn.ubuntu.com/3578-1/
- https://www.debian.org/security/2018/dsa-4125
- https://www.exploit-db.com/exploits/44154/
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=889274
- https://github.com/dbry/WavPack/issues/26
- https://github.com/dbry/WavPack/commit/8e3fe45a7bac31d9a3b558ae0079e2d92a04799e
