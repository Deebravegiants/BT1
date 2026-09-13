# [H] video: fbdev: vesafb: Fix a use-after-free due early fb_info cleanup

## Summary
Severity: High
Advisory: CVE-2022-49419
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49419
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

video: fbdev: vesafb: Fix a use-after-free due early fb_info cleanup

Commit b3c9a924aab6 ("fbdev: vesafb: Cleanup fb_info in .fb_destroy rather
than .remove") fixed a use-after-free error due the vesafb driver freeing
the fb_info in the .remove handler instead of doing it in .fb_destroy.

This can happen if the .fb_destroy callback is executed after the .remove
callback, since the former tries to access a pointer freed by the latter.

But that change didn't take into account that another possible scenario is
that .fb_destroy is called before the .remove callback. For example, if no
process has the fbdev chardev opened by the time the driver is removed.

If that's the case, fb_info will be freed when unregister_framebuffer() is
called, making the fb_info pointer accessed in vesafb_remove() after that
to no longer be valid.

To prevent that, move the expression containing the info->par to happen
before the unregister_framebuffer() function call.

## References
- https://git.kernel.org/stable/c/0fac5f8fb1bc2fc4f8714bf5e743c9cc3f547c63
- https://git.kernel.org/stable/c/acde4003efc16480375543638484d8f13f2e99a3
- https://git.kernel.org/stable/c/d260cad015945d1f4bb9b028a096f648506106a2
- https://git.kernel.org/stable/c/f605f5558ecc175ec70016a3c15f007cb6386531
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49419.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49419
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
