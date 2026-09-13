# [H] drm/connector/hdmi: Fix out of bounds memory read

## Summary
Severity: High
Advisory: CVE-2026-80749
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-80749
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/connector/hdmi: Fix out of bounds memory read

A helper function was copying a given audio infoframe into the
connector's copy but using the size of the destination (a generic
target, sized to accept many different data blocks) not the source (a
very specific type of data block). Thus, it was copying 60 bytes of
data from a 28 byte allocation.

Fix that by using the source size instead, together with a build bug
on the source size actually being smaller than the destination.

I hit this running KUnit tests under KASAN (while debugging something
else entirely). In the real world, it seems unlikely to cause an
actual problem. It is a read not a write so it can't corrupt any
memory. However, it could potentially fall off the end of a page and
cause an accvio bug.

## References
- https://git.kernel.org/stable/c/9ecf8ba763d0ffe0673538eb4bf7806f20455d19
- https://git.kernel.org/stable/c/d9f7454c185c0c7f0973e11d62ad6c06862c324c
- https://git.kernel.org/stable/c/e5b527804a1ea4f70e139179d3062cf5de8c06ab
- https://git.kernel.org/stable/c/f72bb95732bc5ca87b50c52c8f087ba501950809
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80749.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80749
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
