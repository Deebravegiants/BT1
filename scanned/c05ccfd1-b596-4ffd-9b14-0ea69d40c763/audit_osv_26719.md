# [H] clk: Fix memory leak in devm_clk_notifier_register()

## Summary
Severity: High
Advisory: CVE-2023-53674
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2023-53674
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: Fix memory leak in devm_clk_notifier_register()

devm_clk_notifier_register() allocates a devres resource for clk
notifier but didn't register that to the device, so the notifier didn't
get unregistered on device detach and the allocated resource was leaked.

Fix the issue by registering the resource through devres_add().

This issue was found with kmemleak on a Chromebook.

## References
- https://git.kernel.org/stable/c/49451db71b746df990888068961f1033f7c9b734
- https://git.kernel.org/stable/c/7fb933e56f77a57ef7cfc59fc34cbbf1b1fa31ff
- https://git.kernel.org/stable/c/a326cf0107b197e649bbaa2a2b1355894826ce32
- https://git.kernel.org/stable/c/cb1b04fd4283fc8f9acefe0ddc61ba072ed44877
- https://git.kernel.org/stable/c/efbbda79b2881a04dcd0e8f28634933d79e17e49
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53674.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53674
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
