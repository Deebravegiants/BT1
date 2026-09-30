# [M] ASoC: fsl_mqs: move of_node_put() to the correct location

## Summary
Severity: Medium
Advisory: CVE-2023-53268
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53268
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: fsl_mqs: move of_node_put() to the correct location

of_node_put() should have been done directly after
mqs_priv->regmap = syscon_node_to_regmap(gpr_np);
otherwise it creates a reference leak on the success path.

To fix this, of_node_put() is moved to the correct location, and change
all the gotos to direct returns.

## References
- https://git.kernel.org/stable/c/1bdb4a5ccab2316935ce4ad4fd4df8d36f0ffc6e
- https://git.kernel.org/stable/c/1c34890273a020d61d6127ade3f68ed1cb21c16a
- https://git.kernel.org/stable/c/402299cca89273b62384b5f9645ea49cd5fc4a57
- https://git.kernel.org/stable/c/6a129c0e9935112ecf2ffb6de98f83b8fd090c86
- https://git.kernel.org/stable/c/9a2585088a7d6f98a5a910f5b4b74b6d24e63156
- https://git.kernel.org/stable/c/b5a6930fc6a432e32714c4ed3c597077d999cf6d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53268.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53268
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
