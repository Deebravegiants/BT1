# [M] CVE-2021-28693

## Summary
Severity: Medium
Advisory: CVE-2021-28693
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-30
Source: https://osv.dev/vulnerability/CVE-2021-28693
Type: osv

## Details
xen/arm: Boot modules are not scrubbed The bootloader will load boot modules (e.g. kernel, initramfs...) in a temporary area before they are copied by Xen to each domain memory. To ensure sensitive data is not leaked from the modules, Xen must "scrub" them before handing the page over to the allocator. Unfortunately, it was discovered that modules will not be scrubbed on Arm.

## References
- https://xenbits.xenproject.org/xsa/advisory-372.txt
- https://security.gentoo.org/glsa/202107-30
