# [H] xen-netfront: handle NULL returned by xdp_convert_buff_to_frame()

## Summary
Severity: High
Advisory: CVE-2025-37820
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-08
Source: https://osv.dev/vulnerability/CVE-2025-37820
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <6.1.136, >=6.2.0 <6.6.89, >=6.7.0 <6.12.26, >=6.13.0 <6.14.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

xen-netfront: handle NULL returned by xdp_convert_buff_to_frame()

The function xdp_convert_buff_to_frame() may return NULL if it fails
to correctly convert the XDP buffer into an XDP frame due to memory
constraints, internal errors, or invalid data. Failing to check for NULL
may lead to a NULL pointer dereference if the result is used later in
processing, potentially causing crashes, data corruption, or undefined
behavior.

On XDP redirect failure, the associated page must be released explicitly
if it was previously retained via get_page(). Failing to do so may result
in a memory leak, as the pages reference count is not decremented.

## References
- https://git.kernel.org/stable/c/5b83d30c63f9964acb1bc63eb8e670b9e0d2c240
- https://git.kernel.org/stable/c/cc3628dcd851ddd8d418bf0c897024b4621ddc92
- https://git.kernel.org/stable/c/cefd8a2e2de46209ce66e6d30c237eb59b6c5bfa
- https://git.kernel.org/stable/c/d6a9c4e6f9b3ec3ad98468c950ad214af8a2efb9
- https://git.kernel.org/stable/c/eefccd889df3b49d92e7349d94c4aa7e1ba19f6c
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37820.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37820
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
