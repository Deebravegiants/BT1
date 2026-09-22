# [H] phy: ti: tusb1210: Resolve charger-det crash if charger psy is unregistered

## Summary
Severity: High
Advisory: CVE-2024-35986
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-35986
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.90, >=6.2.0 <6.6.30, >=6.7.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

phy: ti: tusb1210: Resolve charger-det crash if charger psy is unregistered

The power_supply frame-work is not really designed for there to be
long living in kernel references to power_supply devices.

Specifically unregistering a power_supply while some other code has
a reference to it triggers a WARN in power_supply_unregister():

	WARN_ON(atomic_dec_return(&psy->use_cnt));

Folllowed by the power_supply still getting removed and the
backing data freed anyway, leaving the tusb1210 charger-detect code
with a dangling reference, resulting in a crash the next time
tusb1210_get_online() is called.

Fix this by only holding the reference in tusb1210_get_online()
freeing it at the end of the function. Note this still leaves
a theoretical race window, but it avoids the issue when manually
rmmod-ing the charger chip driver during development.

## References
- https://git.kernel.org/stable/c/25b3498485ac281e5851700e33b97f12c9533fd8
- https://git.kernel.org/stable/c/73224a5d2180066c7fe05b4656647601ba08d588
- https://git.kernel.org/stable/c/9827caa5105fb16d1fae2e75c8d0e4662014b3ca
- https://git.kernel.org/stable/c/bf6e4ee5c43690e4c5a8a057bbcd4ff986bed052
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35986.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35986
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
