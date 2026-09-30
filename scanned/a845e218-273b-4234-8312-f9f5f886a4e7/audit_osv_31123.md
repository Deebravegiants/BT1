# [H] media: i2c: ds90ub9x3: Fix extra fwnode_handle_put()

## Summary
Severity: High
Advisory: CVE-2024-58003
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-58003
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.78, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: i2c: ds90ub9x3: Fix extra fwnode_handle_put()

The ub913 and ub953 drivers call fwnode_handle_put(priv->sd.fwnode) as
part of their remove process, and if the driver is removed multiple
times, eventually leads to put "overflow", possibly causing memory
corruption or crash.

The fwnode_handle_put() is a leftover from commit 905f88ccebb1 ("media:
i2c: ds90ub9x3: Fix sub-device matching"), which changed the code
related to the sd.fwnode, but missed removing these fwnode_handle_put()
calls.

## References
- https://git.kernel.org/stable/c/474d7baf91d37bc411fa60de5bbf03c9dd82e18a
- https://git.kernel.org/stable/c/60b45ece41c5632a3a3274115a401cb244180646
- https://git.kernel.org/stable/c/70743d6a8b256225675711e7983825f1be86062d
- https://git.kernel.org/stable/c/f4e4373322f8d4c19721831f7fb989e52d30dab0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58003.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58003
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
