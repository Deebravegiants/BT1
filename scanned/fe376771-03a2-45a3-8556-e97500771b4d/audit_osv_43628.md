# [H] fou: Fix use-after-free in fou_create()

## Summary
Severity: High
Advisory: CVE-2026-74496
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74496
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

fou: Fix use-after-free in fou_create()

fou_create() publishes struct fou through sk_user_data before adding the
new FOU port to the per-netns list.  If fou_add_to_port_list() fails,
the error path frees fou while it is still reachable through
sk_user_data.  A concurrent receive can then dereference the freed
object in fou_from_sock().

This ordering issue was previously noted in the linked discussion.

The failure is reachable when local port 0 is requested.  Each socket
binds to a different ephemeral port, but fou_cfg_cmp() compares the
requested port 0 and reports -EALREADY once an entry already exists.

Release the tunnel socket before freeing fou so sk_user_data is cleared
first, and defer reclamation with kfree_rcu() to protect concurrent RCU
readers.  This matches the lifetime handling in fou_release().

## References
- https://git.kernel.org/stable/c/a28d8903bfe76089ea4bbdbff9976965f9ef8107
- https://git.kernel.org/stable/c/b14361aca6350ff7907b0e9903c7b94dc7d5d4a0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74496.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74496
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
