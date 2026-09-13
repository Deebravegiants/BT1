# [H] crypto: cavium - prevent integer overflow loading firmware

## Summary
Severity: High
Advisory: CVE-2022-50330
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50330
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <4.14.296, >=4.15.0 <4.19.262, >=4.20.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: cavium - prevent integer overflow loading firmware

The "code_length" value comes from the firmware file.  If your firmware
is untrusted realistically there is probably very little you can do to
protect yourself.  Still we try to limit the damage as much as possible.
Also Smatch marks any data read from the filesystem as untrusted and
prints warnings if it not capped correctly.

The "ntohl(ucode->code_length) * 2" multiplication can have an
integer overflow.

## References
- https://git.kernel.org/stable/c/172c8a24fc8312cf6b88d3c88469653fdcb1c127
- https://git.kernel.org/stable/c/2526d6bf27d15054bb0778b2f7bc6625fd934905
- https://git.kernel.org/stable/c/371fa5129af53a79f6dddc90fe5bb0825cbe72a4
- https://git.kernel.org/stable/c/3a720eb89026c5241b8c4abb33370dc6fb565eee
- https://git.kernel.org/stable/c/584561e94260268abe1c83e00d9c205565cb7bc5
- https://git.kernel.org/stable/c/90e483e7f20c32287d2a9da967e122938f52737a
- https://git.kernel.org/stable/c/c4d4c2afd08dfb3cd1c880d1811ede2568e81a6d
- https://git.kernel.org/stable/c/e29fd7a6852376d2cfb95ad5d6d3eeff93f815e9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50330.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50330
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
