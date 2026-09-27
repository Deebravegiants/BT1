# [C] In libarchive before 3.6.2, the software does not check for an error after calling calloc function...

## Summary
Severity: Critical
Advisory: JLSEC-2025-237
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-237
Type: osv

## Affected
- Julia: `LibArchive_jll` — affected >=0 <3.7.4+0

## Details
In libarchive before 3.6.2, the software does not check for an error after calling calloc function that can return with a NULL pointer if the function fails, which leads to a resultant NULL pointer dereference. NOTE: the discoverer cites this CWE-476 remark but third parties dispute the code-execution impact: "In rare circumstances, when NULL is equivalent to the 0x0 memory address and privileged code can access it, then writing or reading memory is possible, which may lead to code execution."

## References
- https://bugs.gentoo.org/882521
- https://github.com/libarchive/libarchive/blob/v3.0.0a/libarchive/archive_write.c#L215
- https://github.com/libarchive/libarchive/issues/1754
- https://lists.debian.org/debian-lts-announce/2023/01/msg00034.html
- https://lists.debian.org/debian-lts-announce/2024/11/msg00007.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/V67OO2UUQAUJS3IK4JZPF6F3LUCBU6IS/
- https://security.gentoo.org/glsa/202309-14
