# [H] lz4: fix LZ4_decompress_safe_partial read out of bound

## Summary
Severity: High
Advisory: CVE-2022-49078
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49078
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.189, >=5.5.0 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

lz4: fix LZ4_decompress_safe_partial read out of bound

When partialDecoding, it is EOF if we've either filled the output buffer
or can't proceed with reading an offset for following match.

In some extreme corner cases when compressed data is suitably corrupted,
UAF will occur.  As reported by KASAN [1], LZ4_decompress_safe_partial
may lead to read out of bound problem during decoding.  lz4 upstream has
fixed it [2] and this issue has been disscussed here [3] before.

current decompression routine was ported from lz4 v1.8.3, bumping
lib/lz4 to v1.9.+ is certainly a huge work to be done later, so, we'd
better fix it first.

[1] https://lore.kernel.org/all/000000000000830d1205cf7f0477@google.com/
[2] https://github.com/lz4/lz4/commit/c5d6f8a8be3927c0bec91bcc58667a6cfad244ad#
[3] https://lore.kernel.org/all/CC666AE8-4CA4-4951-B6FB-A2EFDE3AC03B@fb.com/

## References
- https://git.kernel.org/stable/c/467d5e200ab4486b744fe1776154a43d1aa22d4b
- https://git.kernel.org/stable/c/6adc01a7aa37445dafe8846faa0610a86029b253
- https://git.kernel.org/stable/c/73953dfa9d50e5c9fe98ee13fd1d3427aa12a0a3
- https://git.kernel.org/stable/c/9fb8bc6cfc58773ce95414e11c9ccc8fc6ac4927
- https://git.kernel.org/stable/c/e64dbe97c05c769525cbca099ddbd22485630235
- https://git.kernel.org/stable/c/eafc0a02391b7b36617b36c97c4b5d6832cf5e24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49078.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49078
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
