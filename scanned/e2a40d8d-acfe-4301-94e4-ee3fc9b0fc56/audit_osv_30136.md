# [M] x86: fix user address masking non-canonical speculation issue

## Summary
Severity: Medium
Advisory: CVE-2024-50102
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50102
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86: fix user address masking non-canonical speculation issue

It turns out that AMD has a "Meltdown Lite(tm)" issue with non-canonical
accesses in kernel space.  And so using just the high bit to decide
whether an access is in user space or kernel space ends up with the good
old "leak speculative data" if you have the right gadget using the
result:

  CVE-2020-12965 “Transient Execution of Non-Canonical Accesses“

Now, the kernel surrounds the access with a STAC/CLAC pair, and those
instructions end up serializing execution on older Zen architectures,
which closes the speculation window.

But that was true only up until Zen 5, which renames the AC bit [1].
That improves performance of STAC/CLAC a lot, but also means that the
speculation window is now open.

Note that this affects not just the new address masking, but also the
regular valid_user_address() check used by access_ok(), and the asm
version of the sign bit check in the get_user() helpers.

It does not affect put_user() or clear_user() variants, since there's no
speculative result to be used in a gadget for those operations.

## References
- https://git.kernel.org/stable/c/291313693677a345d4f50aae3c68e28b469f601e
- https://git.kernel.org/stable/c/86e6b1547b3d013bc392adf775b89318441403c2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50102.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50102
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
