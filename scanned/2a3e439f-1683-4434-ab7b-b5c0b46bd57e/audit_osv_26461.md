# [H] phy: hisilicon: Fix an out of bounds check in hisi_inno_phy_probe()

## Summary
Severity: High
Advisory: CVE-2023-53238
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53238
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <4.19.291, >=4.20.0 <5.4.253, >=5.5.0 <5.10.190, >=5.11.0 <5.15.124, >=5.16.0 <6.1.43, >=6.2.0 <6.4.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

phy: hisilicon: Fix an out of bounds check in hisi_inno_phy_probe()

The size of array 'priv->ports[]' is INNO_PHY_PORT_NUM.

In the for loop, 'i' is used as the index for array 'priv->ports[]'
with a check (i > INNO_PHY_PORT_NUM) which indicates that
INNO_PHY_PORT_NUM is allowed value for 'i' in the same loop.

This > comparison needs to be changed to >=, otherwise it potentially leads
to an out of bounds write on the next iteration through the loop

## References
- https://git.kernel.org/stable/c/01cb355bb92e8fcf8306e11a4774d610c5864e39
- https://git.kernel.org/stable/c/13c088cf3657d70893d75cf116be937f1509cc0f
- https://git.kernel.org/stable/c/195e806b2afb0bad6470c9094f7e45e0cf109ee0
- https://git.kernel.org/stable/c/2843a2e703f5cb85c9eeca11b7ee90861635a010
- https://git.kernel.org/stable/c/6d8a71e4c3a2fa4960cc50996e76a42b62fab677
- https://git.kernel.org/stable/c/ad249aa3c38f329f91fba8b4b3cd087e79fb0ce8
- https://git.kernel.org/stable/c/ce69eac840db0b559994dc4290fce3d7c0d7bccd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53238.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53238
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
