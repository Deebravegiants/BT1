# [H] CVE-2018-6767

## Summary
Severity: High
Advisory: CVE-2018-6767
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-06
Source: https://osv.dev/vulnerability/CVE-2018-6767
Type: osv

## Details
A stack-based buffer over-read in the ParseRiffHeaderConfig function of cli/riff.c file of WavPack 5.1.0 allows a remote attacker to cause a denial-of-service attack or possibly have unspecified other impact via a maliciously crafted RF64 file.

## References
- http://packetstormsecurity.com/files/155743/Slackware-Security-Advisory-wavpack-Updates.html
- https://seclists.org/bugtraq/2019/Dec/37
- https://usn.ubuntu.com/3568-1/
- https://www.debian.org/security/2018/dsa-4125
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=889276
- https://github.com/dbry/WavPack/issues/27
- https://github.com/dbry/WavPack/commit/d5bf76b5a88d044a1be1d5656698e3ba737167e5
