# [H] Input: imx_sc_key - fix memory corruption on unload

## Summary
Severity: High
Advisory: CVE-2025-40262
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-40262
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.118, >=6.7.0 <6.12.60, >=6.13.0 <6.17.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: imx_sc_key - fix memory corruption on unload

This is supposed to be "priv" but we accidentally pass "&priv" which is
an address in the stack and so it will lead to memory corruption when
the imx_sc_key_action() function is called.  Remove the &.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://git.kernel.org/stable/c/3e96803b169dc948847f0fc2bae729a80914eb7b
- https://git.kernel.org/stable/c/4ce5218b101205b3425099fe3df88a61b58f9cc2
- https://git.kernel.org/stable/c/56881294915a6e866d31a46f9bcb5e19167cfbaa
- https://git.kernel.org/stable/c/6524a15d33951b18ac408ebbcb9c16e14e21c336
- https://git.kernel.org/stable/c/a155292c3ce722036014da5477ee0e4c87b5e6b3
- https://git.kernel.org/stable/c/ca9a08de9b294422376f47ade323d69590dbc6f2
- https://git.kernel.org/stable/c/d83f1512758f4ef6fc5e83219fe7eeeb6b428ea4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40262.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40262
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
