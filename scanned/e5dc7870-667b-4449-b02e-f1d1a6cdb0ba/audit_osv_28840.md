# [M] Reapply "drm/qxl: simplify qxl_fence_wait"

## Summary
Severity: Medium
Advisory: CVE-2024-36944
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36944
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.156 <5.15.159, >=6.1.87 <6.1.91, >=6.6.28 <6.6.31, >=6.8.7 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Reapply "drm/qxl: simplify qxl_fence_wait"

This reverts commit 07ed11afb68d94eadd4ffc082b97c2331307c5ea.

Stephen Rostedt reports:
 "I went to run my tests on my VMs and the tests hung on boot up.
  Unfortunately, the most I ever got out was:

  [   93.607888] Testing event system initcall: OK
  [   93.667730] Running tests on all trace events:
  [   93.669757] Testing all events: OK
  [   95.631064] ------------[ cut here ]------------
  Timed out after 60 seconds"

and further debugging points to a possible circular locking dependency
between the console_owner locking and the worker pool locking.

Reverting the commit allows Steve's VM to boot to completion again.

[ This may obviously result in the "[TTM] Buffer eviction failed"
  messages again, which was the reason for that original revert. But at
  this point this seems preferable to a non-booting system... ]

## References
- https://git.kernel.org/stable/c/148ed8b4d64f94ab079c8f0d88c3f444db97ba97
- https://git.kernel.org/stable/c/3628e0383dd349f02f882e612ab6184e4bb3dc10
- https://git.kernel.org/stable/c/3dfe35d8683daf9ba69278643efbabe40000bbf6
- https://git.kernel.org/stable/c/4a89ac4b0921c4ea21eb1b4cf3a469a91bacfcea
- https://git.kernel.org/stable/c/b548c53bc3ab83dc6fc86c8e840f013b2032267a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36944.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36944
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
