# [C] cifs: Fix buffer overflow when parsing NFS reparse points

## Summary
Severity: Critical
Advisory: CVE-2024-49996
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49996
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: Fix buffer overflow when parsing NFS reparse points

ReparseDataLength is sum of the InodeType size and DataBuffer size.
So to get DataBuffer size it is needed to subtract InodeType's size from
ReparseDataLength.

Function cifs_strndup_from_utf16() is currentlly accessing buf->DataBuffer
at position after the end of the buffer because it does not subtract
InodeType size from the length. Fix this problem and correctly subtract
variable len.

Member InodeType is present only when reparse buffer is large enough. Check
for ReparseDataLength before accessing InodeType to prevent another invalid
memory access.

Major and minor rdev values are present also only when reparse buffer is
large enough. Check for reparse buffer size before calling reparse_mkdev().

## References
- https://git.kernel.org/stable/c/01cdddde39b065074fd48f07027757783cbf5b7d
- https://git.kernel.org/stable/c/73b078e3314d4854fd8286f3ba65c860ddd3a3dd
- https://git.kernel.org/stable/c/7b222d6cb87077faf56a687a72af1951cf78c8a9
- https://git.kernel.org/stable/c/803b3a39cb096d8718c0aebc03fd19f11c7dc919
- https://git.kernel.org/stable/c/c173d47b69f07cd7ca08efb4e458adbd4725d8e9
- https://git.kernel.org/stable/c/c6db81c550cea0c73bd72ef55f579991e0e4ba07
- https://git.kernel.org/stable/c/e2a8910af01653c1c268984855629d71fb81f404
- https://git.kernel.org/stable/c/ec79e6170bcae8a6036a4b6960f5e7e59a785601
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49996.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49996
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
