# [C] ksmbd: use opener credentials for delete-on-close

## Summary
Severity: Critical
Advisory: CVE-2026-64392
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64392
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: use opener credentials for delete-on-close

Delete-on-close can be completed by deferred or durable handle teardown,
where no request work is available. Both the base-file unlink and the ADS
xattr removal consequently run with the ksmbd worker credentials and can
bypass filesystem permission checks.

Run both operations with the credentials captured in struct file when the
handle was opened. This preserves the authenticated user's fsuid, fsgid,
supplementary groups and capability restrictions at final close.

## References
- https://git.kernel.org/stable/c/18c59109bb6fb816d5102171666f87cf1e29901d
- https://git.kernel.org/stable/c/4b7059974549d278e30fe70e2a4e421f9839817d
- https://git.kernel.org/stable/c/52e2f21911158ec961cd5aae19c56460db382af0
- https://git.kernel.org/stable/c/e72c15085b6d86f45d224d98aa75b5cace4aaab9
- https://git.kernel.org/stable/c/f08b3f451f12eee4abd8a5981803bc36db84458b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64392.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64392
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
