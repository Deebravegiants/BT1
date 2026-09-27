# [H] CVE-2018-12934

## Summary
Severity: High
Advisory: CVE-2018-12934
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-28
Source: https://osv.dev/vulnerability/CVE-2018-12934
Type: osv

## Details
remember_Ktype in cplus-dem.c in GNU libiberty, as distributed in GNU Binutils 2.30, allows attackers to trigger excessive memory consumption (aka OOM). This can occur during execution of cxxfilt.

## References
- https://usn.ubuntu.com/4326-1/
- https://usn.ubuntu.com/4336-1/
- https://bugs.launchpad.net/ubuntu/+source/binutils/+bug/1763101
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=85453
- https://sourceware.org/bugzilla/show_bug.cgi?id=23059
