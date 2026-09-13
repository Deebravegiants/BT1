# [H] smb/server: fix refcount leak in parse_durable_handle_context()

## Summary
Severity: High
Advisory: CVE-2025-71204
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2025-71204
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.124, >=6.7.0 <6.12.70, >=6.9.0 <6.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb/server: fix refcount leak in parse_durable_handle_context()

When the command is a replay operation and -ENOEXEC is returned,
the refcount of ksmbd_file must be released.

## References
- https://git.kernel.org/stable/c/07df5ff4f6490a5c96715b7c562e0b2908422e04
- https://git.kernel.org/stable/c/3296c3012a9d9a27e81e34910384e55a6ff3cff0
- https://git.kernel.org/stable/c/70dd3513ed6ac8c6cab23f72c5b19f44ca89de9d
- https://git.kernel.org/stable/c/8a15107c4c031fb19737bf2eb4000f847f1d5e4c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71204.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71204
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
