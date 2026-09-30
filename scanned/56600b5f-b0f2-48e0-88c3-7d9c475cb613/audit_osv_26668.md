# [H] udf: Do not bother merging very long extents

## Summary
Severity: High
Advisory: CVE-2023-53506
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53506
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.14.308, >=4.15.0 <4.19.276, >=4.20.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

udf: Do not bother merging very long extents

When merging very long extents we try to push as much length as possible
to the first extent. However this is unnecessarily complicated and not
really worth the trouble. Furthermore there was a bug in the logic
resulting in corrupting extents in the file as syzbot reproducer shows.
So just don't bother with the merging of extents that are too long
together.

## References
- https://git.kernel.org/stable/c/3d20e3b768aff32112bdce8d3219d923ae75f9f1
- https://git.kernel.org/stable/c/53cafe1d6d8ef9f93318e5bfccc0d24f27d41ced
- https://git.kernel.org/stable/c/5d029799d381a9ee06209a222cae75f04c5d5304
- https://git.kernel.org/stable/c/7a965da79f2d22601f329cbfce588386b0847544
- https://git.kernel.org/stable/c/965982feb333aefa9256c0fe188b5f1b958aef63
- https://git.kernel.org/stable/c/9a8d602f0723586e668bae7e65c832ceb9bcc8bc
- https://git.kernel.org/stable/c/adac9ac6d2e04ea0782b91a00ba10706002f3ec4
- https://git.kernel.org/stable/c/d52252a1de4cf96a34f722b0cd8902d8ff78eb57
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53506.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53506
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
