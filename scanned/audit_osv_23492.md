# [H] NFC: nci: Bounds check struct nfc_target arrays

## Summary
Severity: High
Advisory: CVE-2022-48967
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-48967
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.4.0 <4.9.336, >=4.10.0 <4.14.302, >=4.15.0 <4.19.269, >=4.20.0 <5.4.227, >=5.5.0 <5.10.159, >=5.11.0 <5.15.83, >=5.16.0 <6.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFC: nci: Bounds check struct nfc_target arrays

While running under CONFIG_FORTIFY_SOURCE=y, syzkaller reported:

  memcpy: detected field-spanning write (size 129) of single field "target->sensf_res" at net/nfc/nci/ntf.c:260 (size 18)

This appears to be a legitimate lack of bounds checking in
nci_add_new_protocol(). Add the missing checks.

## References
- https://git.kernel.org/stable/c/27eb2d7a1b9987b6d0429b7716b1ff3b82c4ffc9
- https://git.kernel.org/stable/c/6778434706940b8fad7ef35f410d2b9929f256d2
- https://git.kernel.org/stable/c/6b37f0dc0638d13a006f2f24d2f6ca61e83bc714
- https://git.kernel.org/stable/c/908b2da426fe9c3ce74cf541ba40e7a4251db191
- https://git.kernel.org/stable/c/cff35329070b96b4484d23f9f48a5ca2c947e750
- https://git.kernel.org/stable/c/dbdcfb9f6748218a149f62468d6297ce3f014e9c
- https://git.kernel.org/stable/c/e329e71013c9b5a4535b099208493c7826ee4a64
- https://git.kernel.org/stable/c/f41547546db9af99da2c34e3368664d7a79cefae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48967.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48967
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
