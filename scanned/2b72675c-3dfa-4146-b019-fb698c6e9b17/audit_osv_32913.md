# [H] IB/cm: Drop lockdep assert and WARN when freeing old msg

## Summary
Severity: High
Advisory: CVE-2025-38287
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38287
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

IB/cm: Drop lockdep assert and WARN when freeing old msg

The send completion handler can run after cm_id has advanced to another
message.  The cm_id lock is not needed in this case, but a recent change
re-used cm_free_priv_msg(), which asserts that the lock is held and
WARNs if the cm_id's currently outstanding msg is different than the one
being freed.

## References
- https://git.kernel.org/stable/c/7590649ee7af381a9d1153143026dec124c5798e
- https://git.kernel.org/stable/c/fc096a0cd2017cb0aa1e7fb83131410af9283910
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38287.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38287
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
