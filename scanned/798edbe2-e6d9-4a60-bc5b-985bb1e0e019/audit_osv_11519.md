# [M] CVE-2017-8327

## Summary
Severity: Medium
Advisory: CVE-2017-8327
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-29
Source: https://osv.dev/vulnerability/CVE-2017-8327
Type: osv

## Details
The bmpr_read_uncompressed function in imagew-bmp.c in libimageworsener.a in ImageWorsener before 1.3.1 allows remote attackers to cause a denial of service (memory consumption) via a crafted image.

## References
- https://security.gentoo.org/glsa/201706-06
- https://blogs.gentoo.org/ago/2017/04/27/imageworsener-memory-allocation-failure-in-my_mallocfn-imagew-cmd-c/
- https://github.com/jsummers/imageworsener/commit/86564051db45b466e5f667111ce00b5eeedc8fb6
