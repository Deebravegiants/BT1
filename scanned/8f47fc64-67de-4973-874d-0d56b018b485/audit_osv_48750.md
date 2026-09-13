# [C] CVE-2018-12387

## Summary
Severity: Critical
Advisory: CVE-2018-12387
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2018-10-18
Source: https://osv.dev/vulnerability/CVE-2018-12387
Type: osv

## Details
A vulnerability where the JavaScript JIT compiler inlines Array.prototype.push with multiple arguments that results in the stack pointer being off by 8 bytes after a bailout. This leaks a memory address to the calling function which can be used as part of an exploit inside the sandboxed content process. This vulnerability affects Firefox ESR < 60.2.2 and Firefox < 62.0.3.

## References
- http://www.securityfocus.com/bid/105460
- https://access.redhat.com/errata/RHSA-2018:2881
- https://access.redhat.com/errata/RHSA-2018:2884
- https://security.gentoo.org/glsa/201810-01
- https://usn.ubuntu.com/3778-1/
- https://www.mozilla.org/security/advisories/mfsa2018-24/
- http://www.securitytracker.com/id/1041770
- https://www.debian.org/security/2018/dsa-4310
- https://bugzilla.mozilla.org/show_bug.cgi?id=1493903
