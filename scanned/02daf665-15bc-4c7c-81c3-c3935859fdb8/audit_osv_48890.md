# [C] CVE-2018-17141

## Summary
Severity: Critical
Advisory: CVE-2018-17141
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-21
Source: https://osv.dev/vulnerability/CVE-2018-17141
Type: osv

## Details
HylaFAX 6.0.6 and HylaFAX+ 5.6.0 allow remote attackers to execute arbitrary code via a dial-in session that provides a FAX page with the JPEG bit enabled, which is mishandled in FaxModem::writeECMData() in the faxd/CopyQuality.c++ file.

## References
- http://git.hylafax.org/HylaFAX?a=commit%3Bh=c6cac8d8cd0dbe313689ba77023e12bc5b3027be
- https://lists.debian.org/debian-lts-announce/2018/09/msg00026.html
- https://www.debian.org/security/2018/dsa-4298
- http://www.openwall.com/lists/oss-security/2018/09/20/1
- https://seclists.org/bugtraq/2018/Sep/49
- https://www.x41-dsec.de/lab/advisories/x41-2018-008-hylafax/
