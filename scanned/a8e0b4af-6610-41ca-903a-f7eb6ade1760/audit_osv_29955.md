# [M] dlm: fix possible lkb_resource null dereference

## Summary
Severity: Medium
Advisory: CVE-2024-47809
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-47809
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <5.15.209, >=5.16.0 <6.1.167, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dlm: fix possible lkb_resource null dereference

This patch fixes a possible null pointer dereference when this function is
called from request_lock() as lkb->lkb_resource is not assigned yet,
only after validate_lock_args() by calling attach_lkb(). Another issue
is that a resource name could be a non printable bytearray and we cannot
assume to be ASCII coded.

The log functionality is probably never being hit when DLM is used in
normal way and no debug logging is enabled. The null pointer dereference
can only occur on a new created lkb that does not have the resource
assigned yet, it probably never hits the null pointer dereference but we
should be sure that other changes might not change this behaviour and we
actually can hit the mentioned null pointer dereference.

In this patch we just drop the printout of the resource name, the lkb id
is enough to make a possible connection to a resource name if this
exists.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/2db11504ef82a60c1a2063ba7431a5cd013ecfcb
- https://git.kernel.org/stable/c/6fbdc3980b70e9c1c86eccea7d5ee68108008fa7
- https://git.kernel.org/stable/c/8d55ce46dd543c6965970ce70c22c3076dd35b1e
- https://git.kernel.org/stable/c/b98333c67daf887c724cd692e88e2db9418c0861
- https://git.kernel.org/stable/c/e1ffea6bec96d4349dbfcc42ad3e436259f64243
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47809.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47809
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
