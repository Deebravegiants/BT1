# [H] ubifs: Set page uptodate in the correct place

## Summary
Severity: High
Advisory: CVE-2024-35821
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35821
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.27 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ubifs: Set page uptodate in the correct place

Page cache reads are lockless, so setting the freshly allocated page
uptodate before we've overwritten it with the data it's supposed to have
in it will allow a simultaneous reader to see old data.  Move the call
to SetPageUptodate into ubifs_write_end(), which is after we copied the
new data into the page.

## References
- https://git.kernel.org/stable/c/142d87c958d9454c3cffa625fab56f3016e8f9f3
- https://git.kernel.org/stable/c/17772bbe9cfa972ea1ff827319f6e1340de76566
- https://git.kernel.org/stable/c/4aa554832b9dc9e66249df75b8f447d87853e12e
- https://git.kernel.org/stable/c/4b7c4fc60d6a46350fbe54f5dc937aeaa02e675e
- https://git.kernel.org/stable/c/723012cab779eee8228376754e22c6594229bf8f
- https://git.kernel.org/stable/c/778c6ad40256f1c03244fc06d7cdf71f6b5e7310
- https://git.kernel.org/stable/c/8f599ab6fabbca4c741107eade70722a98adfd9f
- https://git.kernel.org/stable/c/f19b1023a3758f40791ec166038d6411c8894ae3
- https://git.kernel.org/stable/c/fc99f4e2d2f1ce766c14e98463c2839194ae964f
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35821.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35821
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
