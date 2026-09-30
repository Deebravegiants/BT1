# [H] CVE-2019-15692

## Summary
Severity: High
Advisory: CVE-2019-15692
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-26
Source: https://osv.dev/vulnerability/CVE-2019-15692
Type: osv

## Details
TigerVNC version prior to 1.10.1 is vulnerable to heap buffer overflow. Vulnerability could be triggered from CopyRectDecoder due to incorrect value checks. Exploitation of this vulnerability could potentially result into remote code execution. This attack appear to be exploitable via network connectivity.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00039.html
- https://github.com/TigerVNC/tigervnc/releases/tag/v1.10.1
- https://github.com/CendioOssman/tigervnc/commit/996356b6c65ca165ee1ea46a571c32a1dc3c3821
- https://www.openwall.com/lists/oss-security/2019/12/20/2
