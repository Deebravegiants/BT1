# [H] wifi: brcmfmac: validate bsscfg indices in IF events

## Summary
Severity: High
Advisory: CVE-2026-43110
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43110
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: brcmfmac: validate bsscfg indices in IF events

brcmf_fweh_handle_if_event() validates the firmware-provided interface
index before it touches drvr->iflist[], but it still uses the raw
bsscfgidx field as an array index without a matching range check.

Reject IF events whose bsscfg index does not fit in drvr->iflist[]
before indexing the interface array.

[add missing wifi prefix]

## References
- https://git.kernel.org/stable/c/1ae1e1caa428844e481231f6dbe9b4f475f1d52d
- https://git.kernel.org/stable/c/2ae3ccb78c0a9ef5ee3d80d02ab319ac1d5af734
- https://git.kernel.org/stable/c/304950a467d83678bd0b0f46331882e2ac23b12d
- https://git.kernel.org/stable/c/3ec7437e9d11374105c2c4e47ae671537729d7e6
- https://git.kernel.org/stable/c/9c81bcc2c695e0082012a2a3d36a0eefaa51579c
- https://git.kernel.org/stable/c/9fca68c2512a362cad258e4df12a307bb2ee4b8e
- https://git.kernel.org/stable/c/b329fbcf075949a038045d8e9b86ae3d5bbd8a54
- https://git.kernel.org/stable/c/b427c2b05222db36d32ee141609de6128e9091bb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43110.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43110
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
