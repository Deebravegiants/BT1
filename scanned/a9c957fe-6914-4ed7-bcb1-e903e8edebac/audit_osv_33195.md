# [M] igb: Fix NULL pointer dereference in ethtool loopback test

## Summary
Severity: Medium
Advisory: CVE-2025-39875
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-39875
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

igb: Fix NULL pointer dereference in ethtool loopback test

The igb driver currently causes a NULL pointer dereference when executing
the ethtool loopback test. This occurs because there is no associated
q_vector for the test ring when it is set up, as interrupts are typically
not added to the test rings.

Since commit 5ef44b3cb43b removed the napi_id assignment in
__xdp_rxq_info_reg(), there is no longer a need to pass a napi_id to it.
Therefore, simply use 0 as the last parameter.

## References
- https://git.kernel.org/stable/c/473be7d39efd3be383e9c0c8e44b53508b4ffeb5
- https://git.kernel.org/stable/c/75871a525a596ff4d16c4aebc0018f8d0923c9b1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39875.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39875
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
