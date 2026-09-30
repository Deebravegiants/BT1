# [M] CVE-2021-47158

## Summary
Severity: Medium
Advisory: CVE-2021-47158
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47158
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dsa: sja1105: add error handling in sja1105_setup()

If any of sja1105_static_config_load(), sja1105_clocking_setup() or
sja1105_devlink_setup() fails, we can't just return in the middle of
sja1105_setup() or memory will leak. Add a cleanup path.

## References
- https://git.kernel.org/stable/c/cec279a898a3b004411682f212215ccaea1cd0fb
- https://git.kernel.org/stable/c/dd8609f203448ca6d58ae71461208b3f6b0329b0
- https://git.kernel.org/stable/c/987e4ab8b8a4fcbf783069e03e7524cd39ffd563
