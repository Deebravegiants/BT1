# [C] CVE-2018-12584

## Summary
Severity: Critical
Advisory: CVE-2018-12584
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-16
Source: https://osv.dev/vulnerability/CVE-2018-12584
Type: osv

## Details
The ConnectionBase::preparseNewBytes function in resip/stack/ConnectionBase.cxx in reSIProcate through 1.10.2 allows remote attackers to cause a denial of service (buffer overflow) or possibly execute arbitrary code when TLS communication is enabled.

## References
- http://joachimdezutter.webredirect.org/advisory.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00031.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00029.html
- http://seclists.org/bugtraq/2018/Aug/14
- https://github.com/resiprocate/resiprocate/commit/2cb291191c93c7c4e371e22cb89805a5b31d6608
- https://packetstormsecurity.com/files/148856/reSIProcate-1.10.2-Heap-Overflow.html
- https://www.exploit-db.com/exploits/45174/
