# [H] perf/arm-cmn: Reject unsupported hardware configurations

## Summary
Severity: High
Advisory: CVE-2026-43150
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43150
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.165, >=6.2.0 <6.6.128, >=6.5.0 <6.12.75, >=6.7.0 <6.18.16, >=6.13.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf/arm-cmn: Reject unsupported hardware configurations

So far we've been fairly lax about accepting both unknown CMN models
(at least with a warning), and unknown revisions of those which we
do know, as although things do frequently change between releases,
typically enough remains the same to be somewhat useful for at least
some basic bringup checks. However, we also make assumptions of the
maximum supported sizes and numbers of things in various places, and
there's no guarantee that something new might not be bigger and lead
to nasty array overflows. Make sure we only try to run on things that
actually match our assumptions and so will not risk memory corruption.

We have at least always failed on completely unknown node types, so
update that error message for clarity and consistency too.

## References
- https://git.kernel.org/stable/c/00d69f21ef2ab00e6156c764d89e2b3539eb2f33
- https://git.kernel.org/stable/c/08c7eadd8a934a1968e1aeeee8b61b853b99fb3a
- https://git.kernel.org/stable/c/36c0de02575ce59dfd879eb4ef63d53a68bbf9ce
- https://git.kernel.org/stable/c/7e2c200010aa93fa78201da959b4ac6b9f8fed0b
- https://git.kernel.org/stable/c/a251d866f50b6a4c95901fa722025065679c2eca
- https://git.kernel.org/stable/c/d3e837e11ee9ed08df229272319199003ba00379
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43150.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43150
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
