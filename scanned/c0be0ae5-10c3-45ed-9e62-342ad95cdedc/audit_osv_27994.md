# [M] net: phy: qcom: at803x: fix kernel panic with at8031_probe

## Summary
Severity: Medium
Advisory: CVE-2024-26942
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26942
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: phy: qcom: at803x: fix kernel panic with at8031_probe

On reworking and splitting the at803x driver, in splitting function of
at803x PHYs it was added a NULL dereference bug where priv is referenced
before it's actually allocated and then is tried to write to for the
is_1000basex and is_fiber variables in the case of at8031, writing on
the wrong address.

Fix this by correctly setting priv local variable only after
at803x_probe is called and actually allocates priv in the phydev struct.

## References
- https://git.kernel.org/stable/c/6a4aee277740d04ac0fd54cfa17cc28261932ddc
- https://git.kernel.org/stable/c/a8a296ad9957b845b89bcf48be1cf8c74875ecc3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26942.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26942
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
