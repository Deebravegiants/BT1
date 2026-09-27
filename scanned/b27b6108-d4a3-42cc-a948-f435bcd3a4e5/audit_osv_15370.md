# [H] CVE-2019-15695

## Summary
Severity: High
Advisory: CVE-2019-15695
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-26
Source: https://osv.dev/vulnerability/CVE-2019-15695
Type: osv

## Details
TigerVNC version prior to 1.10.1 is vulnerable to stack buffer overflow, which could be triggered from CMsgReader::readSetCursor. This vulnerability occurs due to insufficient sanitization of PixelFormat. Since remote attacker can choose offset from start of the buffer to start writing his values, exploitation of this vulnerability could potentially result into remote code execution. This attack appear to be exploitable via network connectivity.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00039.html
- https://github.com/CendioOssman/tigervnc/commit/05e28490873a861379c943bf616614b78b558b89
- https://github.com/TigerVNC/tigervnc/releases/tag/v1.10.1
- https://www.openwall.com/lists/oss-security/2019/12/20/2
