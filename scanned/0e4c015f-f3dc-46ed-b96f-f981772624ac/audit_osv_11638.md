# [M] CVE-2017-9202

## Summary
Severity: Medium
Advisory: CVE-2017-9202
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-23
Source: https://osv.dev/vulnerability/CVE-2017-9202
Type: osv

## Details
imagew-cmd.c:854:45 in libimageworsener.a in ImageWorsener 1.3.1 allows remote attackers to cause a denial of service (divide-by-zero error) via a crafted image, related to imagew-api.c.

## References
- https://blogs.gentoo.org/ago/2017/05/20/imageworsener-multiple-vulnerabilities/
- https://github.com/jsummers/imageworsener/commit/dc49c807926b96e503bd7c0dec35119eecd6c6fe
