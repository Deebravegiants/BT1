# [H] fbdev: sisfb: Fix strbuf array overflow

## Summary
Severity: High
Advisory: CVE-2024-50180
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50180
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.57, >=6.7.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: sisfb: Fix strbuf array overflow

The values of the variables xres and yres are placed in strbuf.
These variables are obtained from strbuf1.
The strbuf1 array contains digit characters
and a space if the array contains non-digit characters.
Then, when executing sprintf(strbuf, "%ux%ux8", xres, yres);
more than 16 bytes will be written to strbuf.
It is suggested to increase the size of the strbuf array to 24.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/11c0d49093b82f6c547fd419c41a982d26bdf5ef
- https://git.kernel.org/stable/c/252f147b1826cbb30ae0304cf86b66d3bb12b743
- https://git.kernel.org/stable/c/41cf6f26abe4f491b694c54bd1aa2530369b7510
- https://git.kernel.org/stable/c/433c84c8495008922534c5cafdae6ff970fb3241
- https://git.kernel.org/stable/c/57c4f4db0a194416da237fd09dad9527e00cb587
- https://git.kernel.org/stable/c/688872c4ea4a528cd6a057d545c83506b533ee1f
- https://git.kernel.org/stable/c/889304120ecb2ca30674d89cd4ef15990b6a571c
- https://git.kernel.org/stable/c/9cf14f5a2746c19455ce9cb44341b5527b5e19c3
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50180.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50180
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
