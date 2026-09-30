# [H] crypto: algif_aead - Revert to operating out-of-place

## Summary
Severity: High
Advisory: CVE-2026-31431
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31431
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.10.254, >=5.11.0 <5.15.204, >=5.16.0 <6.1.170, >=6.2.0 <6.6.137, >=6.7.0 <6.12.85, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: algif_aead - Revert to operating out-of-place

This mostly reverts commit 72548b093ee3 except for the copying of
the associated data.

There is no benefit in operating in-place in algif_aead since the
source and destination come from different mappings.  Get rid of
all the complexity added for in-place operation and just copy the
AD directly.

## References
- http://www.openwall.com/lists/oss-security/2026/04/29/23
- http://www.openwall.com/lists/oss-security/2026/04/29/25
- http://www.openwall.com/lists/oss-security/2026/04/29/26
- http://www.openwall.com/lists/oss-security/2026/04/30/10
- http://www.openwall.com/lists/oss-security/2026/04/30/11
- http://www.openwall.com/lists/oss-security/2026/04/30/12
- http://www.openwall.com/lists/oss-security/2026/04/30/14
- http://www.openwall.com/lists/oss-security/2026/04/30/15
- http://www.openwall.com/lists/oss-security/2026/04/30/16
- http://www.openwall.com/lists/oss-security/2026/04/30/17
- http://www.openwall.com/lists/oss-security/2026/04/30/18
- http://www.openwall.com/lists/oss-security/2026/04/30/2
- http://www.openwall.com/lists/oss-security/2026/04/30/20
- http://www.openwall.com/lists/oss-security/2026/04/30/5
- http://www.openwall.com/lists/oss-security/2026/04/30/6
- http://www.openwall.com/lists/oss-security/2026/05/01/10
- http://www.openwall.com/lists/oss-security/2026/05/01/12
- http://www.openwall.com/lists/oss-security/2026/05/01/15
- http://www.openwall.com/lists/oss-security/2026/05/01/16
- http://www.openwall.com/lists/oss-security/2026/05/01/17
