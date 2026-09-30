# [C] nvmet-tcp: add bounds check on Transfer Tag

## Summary
Severity: Critical
Advisory: CVE-2022-50717
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2022-50717
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet-tcp: add bounds check on Transfer Tag

ttag is used as an index to get cmd in nvmet_tcp_handle_h2c_data_pdu(),
add a bounds check to avoid out-of-bounds access.

## References
- https://git.kernel.org/stable/c/0d150ccd55dbfad36f55855b40b381884c98456e
- https://git.kernel.org/stable/c/752593d04637ebdc87fd29cba81897f21ae053f0
- https://git.kernel.org/stable/c/b6a545ffa2c192b1e6da4a7924edac5ba9f4ea2b
- https://git.kernel.org/stable/c/d5bb45f47b37d10f010355686b28c9ebacb361d4
- https://git.kernel.org/stable/c/ec8adf767e1cfa7031f853b8c71ba1963f07df15
- https://git.kernel.org/stable/c/fcf82e4553db911d10234ff2390cfd0e2aa854e4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50717.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50717
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
