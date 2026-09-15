# [H] CVE-2019-15691

## Summary
Severity: High
Advisory: CVE-2019-15691
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-26
Source: https://osv.dev/vulnerability/CVE-2019-15691
Type: osv

## Details
TigerVNC version prior to 1.10.1 is vulnerable to stack use-after-return, which occurs due to incorrect usage of stack memory in ZRLEDecoder. If decoding routine would throw an exception, ZRLEDecoder may try to access stack variable, which has been already freed during the process of stack unwinding. Exploitation of this vulnerability could potentially result into remote code execution. This attack appear to be exploitable via network connectivity.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00039.html
- https://github.com/TigerVNC/tigervnc/releases/tag/v1.10.1
- https://github.com/CendioOssman/tigervnc/commit/d61a767d6842b530ffb532ddd5a3d233119aad40
- https://www.openwall.com/lists/oss-security/2019/12/20/2
