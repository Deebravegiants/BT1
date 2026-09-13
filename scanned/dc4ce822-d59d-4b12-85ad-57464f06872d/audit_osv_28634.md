# [H] md/dm-raid: don't call md_reap_sync_thread() directly

## Summary
Severity: High
Advisory: CVE-2024-35808
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35808
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/dm-raid: don't call md_reap_sync_thread() directly

Currently md_reap_sync_thread() is called from raid_message() directly
without holding 'reconfig_mutex', this is definitely unsafe because
md_reap_sync_thread() can change many fields that is protected by
'reconfig_mutex'.

However, hold 'reconfig_mutex' here is still problematic because this
will cause deadlock, for example, commit 130443d60b1b ("md: refactor
idle/frozen_sync_thread() to fix deadlock").

Fix this problem by using stop_sync_thread() to unregister sync_thread,
like md/raid did.

## References
- https://git.kernel.org/stable/c/347dcdc15a1706f61aa545ae498ededdf31aeebc
- https://git.kernel.org/stable/c/9e59b8d76ff511505eb0dd1478329f09e0f04669
- https://git.kernel.org/stable/c/cd32b27a66db8776d8b8e82ec7d7dde97a8693b0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35808.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35808
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
