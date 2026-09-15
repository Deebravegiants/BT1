# [M] genetlink: fix genl_bind() invoking bind() after -EPERM

## Summary
Severity: Medium
Advisory: CVE-2025-39926
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39926
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.48, >=6.13.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

genetlink: fix genl_bind() invoking bind() after -EPERM

Per family bind/unbind callbacks were introduced to allow families
to track multicast group consumer presence, e.g. to start or stop
producing events depending on listeners.

However, in genl_bind() the bind() callback was invoked even if
capability checks failed and ret was set to -EPERM. This means that
callbacks could run on behalf of unauthorized callers while the
syscall still returned failure to user space.

Fix this by only invoking bind() after "if (ret) break;" check
i.e. after permission checks have succeeded.

## References
- https://git.kernel.org/stable/c/1dbfb0363224f6da56f6655d596dc5097308d6f5
- https://git.kernel.org/stable/c/8858c1e9405906c09589d7c336f04058ea198207
- https://git.kernel.org/stable/c/98c9d884047a3051c203708914a874dece3cbe54
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39926.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39926
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
