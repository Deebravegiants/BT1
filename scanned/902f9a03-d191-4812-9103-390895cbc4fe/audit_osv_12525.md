# [M] CVE-2018-12641

## Summary
Severity: Medium
Advisory: CVE-2018-12641
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-06-22
Source: https://osv.dev/vulnerability/CVE-2018-12641
Type: osv

## Details
An issue was discovered in arm_pt in cplus-dem.c in GNU libiberty, as distributed in GNU Binutils 2.30. Stack Exhaustion occurs in the C++ demangling functions provided by libiberty, and there are recursive stack frames: demangle_arm_hp_template, demangle_class_name, demangle_fund_type, do_type, do_arg, demangle_args, and demangle_nested_args. This can occur during execution of nm-new.

## References
- https://usn.ubuntu.com/4326-1/
- https://usn.ubuntu.com/4336-1/
- https://access.redhat.com/errata/RHSA-2019:2075
- https://bugs.launchpad.net/ubuntu/+source/binutils/+bug/1763099
- https://security.gentoo.org/glsa/201908-01
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=85452
- https://sourceware.org/bugzilla/show_bug.cgi?id=23058
