# [M] ALSA: hda: Fix Oops by 9.1 surround channel names

## Summary
Severity: Medium
Advisory: CVE-2023-53400
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53400
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <4.14.316, >=4.15.0 <4.19.284, >=4.20.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: hda: Fix Oops by 9.1 surround channel names

get_line_out_pfx() may trigger an Oops by overflowing the static array
with more than 8 channels.  This was reported for MacBookPro 12,1 with
Cirrus codec.

As a workaround, extend for the 9.1 channels and also fix the
potential Oops by unifying the code paths accessing the same array
with the proper size check.

## References
- https://git.kernel.org/stable/c/082dcd51667b29097500c824c37f24da997a6a8a
- https://git.kernel.org/stable/c/3b44ec8c5c44790a82f07e90db45643c762878c6
- https://git.kernel.org/stable/c/4ef155ddf9578bf035964d58739fdcd7dd44b4a4
- https://git.kernel.org/stable/c/546b1f5f45a355ae0d3a8041cdaca597dfcac825
- https://git.kernel.org/stable/c/b5694aae4c2d9a288bafce7d38f122769e0428e6
- https://git.kernel.org/stable/c/dc8c569d59f17b17d7bca4f68c36bd571659921e
- https://git.kernel.org/stable/c/e8c7d7c43d5edd20e518fe1dfb2371d1fe6e8bb8
- https://git.kernel.org/stable/c/fcf637461019e9a5a0c12fc5c42a9db1779b0634
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53400.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53400
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
