# [H] smb/server: fix possible refcount leak in smb2_sess_setup()

## Summary
Severity: High
Advisory: CVE-2025-40285
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-06
Source: https://osv.dev/vulnerability/CVE-2025-40285
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.59, >=6.13.0 <6.17.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb/server: fix possible refcount leak in smb2_sess_setup()

Reference count of ksmbd_session will leak when session need reconnect.
Fix this by adding the missing ksmbd_user_session_put().

## References
- https://git.kernel.org/stable/c/379510a815cb2e64eb0a379cb62295d6ade65df0
- https://git.kernel.org/stable/c/6fc935f798d44a8eb8a5e6659198399fbf57b981
- https://git.kernel.org/stable/c/d37b2c81c83d6c0d5ca582f4fe73c672983f9e0d
- https://git.kernel.org/stable/c/dcc51dfe6ff26b52cac106865a172ac982d78401
- https://git.kernel.org/stable/c/e671f9bb97805771380c98de944e2ceab6949188
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40285.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40285
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
