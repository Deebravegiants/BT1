# [C] net: bcmgenet: fix off-by-one in bcmgenet_put_txcb

## Summary
Severity: Critical
Advisory: CVE-2026-53088
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53088
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: bcmgenet: fix off-by-one in bcmgenet_put_txcb

The write_ptr points to the next open tx_cb. We want to return the
tx_cb that gets rewinded, so we must rewind the pointer first then
return the tx_cb that it points to. That way the txcb can be correctly
cleaned up.

## References
- https://git.kernel.org/stable/c/14e9f86564fff7bcf7f45c1b69080e837b31d185
- https://git.kernel.org/stable/c/29394f722f620281f2ee9a47f947734e53d72c90
- https://git.kernel.org/stable/c/2a74590170427a3ca7cc4bb8690cdd559129c29c
- https://git.kernel.org/stable/c/4cab761fc51c65aef741fcece4a18f3554edbc09
- https://git.kernel.org/stable/c/57f3f53d2c9c5a9e133596e2f7bc1c50688a6d38
- https://git.kernel.org/stable/c/72df896e31ddd06fcc5a789f025ad7a62a18bc9b
- https://git.kernel.org/stable/c/85f34ec320d3881badfd4edc5fee5cd5012bb54d
- https://git.kernel.org/stable/c/fb9a3c1f547d0ff024dbfe7b6f327626ddf0a3de
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53088.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53088
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
