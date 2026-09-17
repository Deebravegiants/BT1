# [H] ALSA: emux: improve patch ioctl data validation

## Summary
Severity: High
Advisory: CVE-2024-42097
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-42097
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.317, >=4.20.0 <5.4.279, >=5.5.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.97, >=6.2.0 <6.6.37, >=6.7.0 <6.9.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: emux: improve patch ioctl data validation

In load_data(), make the validation of and skipping over the main info
block match that in load_guspatch().

In load_guspatch(), add checking that the specified patch length matches
the actually supplied data, like load_data() already did.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/40d7def67841343c10f8642a41031fecbb248bab
- https://git.kernel.org/stable/c/79d9a000f0220cdaba1682d2a23c0d0c61d620a3
- https://git.kernel.org/stable/c/7a18293fd8d8519c2f7a03753bc1583b18e3db69
- https://git.kernel.org/stable/c/87039b83fb7bfd7d0e0499aaa8e6c049906b4d14
- https://git.kernel.org/stable/c/89b32ccb12ae67e630c6453d778ec30a592a212f
- https://git.kernel.org/stable/c/d0ff2443fcbb472206d45a5d2a90cc694065804e
- https://git.kernel.org/stable/c/d23982ea9aa438f35a8c8a6305943e98a8db90f6
- https://git.kernel.org/stable/c/d8f5ce3cb9adf0c72e2ad6089aba02d7a32469c2
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42097.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42097
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
