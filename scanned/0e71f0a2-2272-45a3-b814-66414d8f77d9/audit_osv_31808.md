# [H] driver core: class: Fix wild pointer dereferences in API class_dev_iter_next()

## Summary
Severity: High
Advisory: CVE-2025-21810
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21810
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

driver core: class: Fix wild pointer dereferences in API class_dev_iter_next()

There are a potential wild pointer dereferences issue regarding APIs
class_dev_iter_(init|next|exit)(), as explained by below typical usage:

// All members of @iter are wild pointers.
struct class_dev_iter iter;

// class_dev_iter_init(@iter, @class, ...) checks parameter @class for
// potential class_to_subsys() error, and it returns void type and does
// not initialize its output parameter @iter, so caller can not detect
// the error and continues to invoke class_dev_iter_next(@iter) even if
// @iter still contains wild pointers.
class_dev_iter_init(&iter, ...);

// Dereference these wild pointers in @iter here once suffer the error.
while (dev = class_dev_iter_next(&iter)) { ... };

// Also dereference these wild pointers here.
class_dev_iter_exit(&iter);

Actually, all callers of these APIs have such usage pattern in kernel tree.
Fix by:
- Initialize output parameter @iter by memset() in class_dev_iter_init()
  and give callers prompt by pr_crit() for the error.
- Check if @iter is valid in class_dev_iter_next().

## References
- https://git.kernel.org/stable/c/1614e75d1a1b63db6421c7a4bf37004720c7376c
- https://git.kernel.org/stable/c/5c504e9767b947cf7d4e29b811c0c8b3c53242b7
- https://git.kernel.org/stable/c/e128f82f7006991c99a58114f70ef61e937b1ac1
- https://git.kernel.org/stable/c/f4b9bc823b0cfdebfed479c0e87d6939c7562e87
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21810.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21810
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
