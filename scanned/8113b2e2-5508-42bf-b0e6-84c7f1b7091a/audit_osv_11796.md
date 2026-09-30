# [H] CVE-2017-9766

## Summary
Severity: High
Advisory: CVE-2017-9766
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-21
Source: https://osv.dev/vulnerability/CVE-2017-9766
Type: osv

## Details
In Wireshark 2.2.7, PROFINET IO data with a high recursion depth allows remote attackers to cause a denial of service (stack exhaustion) in the dissect_IODWriteReq function in plugins/profinet/packet-dcerpc-pn-io.c.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=d6e888400ba64de3147d1111a4c23edf389b0000
- http://www.securityfocus.com/bid/99187
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13811
