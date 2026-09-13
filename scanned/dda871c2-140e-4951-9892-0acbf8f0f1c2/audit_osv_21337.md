# [H] CVE-2021-42341

## Summary
Severity: High
Advisory: CVE-2021-42341
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-14
Source: https://osv.dev/vulnerability/CVE-2021-42341
Type: osv

## Details
checkpath in OpenRC before 0.44.7 uses the direct output of strlen() to allocate strings, which does not account for the '\0' byte at the end of the string. This results in memory corruption. CVE-2021-42341 was introduced in git commit 63db2d99e730547339d1bdd28e8437999c380cae, which was introduced as part of OpenRC 0.44.0 development.

## References
- https://bugs.gentoo.org/816900
- https://github.com/OpenRC/openrc/commit/63db2d99e730547339d1bdd28e8437999c380cae
- https://github.com/OpenRC/openrc/commit/bb8334104baf4d5a4a442a8647fb9204738f2204
- https://github.com/OpenRC/openrc/issues/418
- https://github.com/OpenRC/openrc/issues/459
- https://github.com/OpenRC/openrc/pull/462
