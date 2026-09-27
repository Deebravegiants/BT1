# [H] CVE-2018-7253

## Summary
Severity: High
Advisory: CVE-2018-7253
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-19
Source: https://osv.dev/vulnerability/CVE-2018-7253
Type: osv

## Details
The ParseDsdiffHeaderConfig function of the cli/dsdiff.c file of WavPack 5.1.0 allows a remote attacker to cause a denial-of-service (heap-based buffer over-read) or possibly overwrite the heap via a maliciously crafted DSDIFF file.

## References
- http://packetstormsecurity.com/files/155743/Slackware-Security-Advisory-wavpack-Updates.html
- https://seclists.org/bugtraq/2019/Dec/37
- https://usn.ubuntu.com/3578-1/
- https://www.debian.org/security/2018/dsa-4125
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=889559
- https://github.com/dbry/WavPack/commit/36a24c7881427d2e1e4dc1cef58f19eee0d13aec
- https://github.com/dbry/WavPack/issues/28
