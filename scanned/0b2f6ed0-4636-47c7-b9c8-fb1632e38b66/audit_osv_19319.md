# [M] CVE-2021-20197

## Summary
Severity: Medium
Advisory: CVE-2021-20197
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-03-26
Source: https://osv.dev/vulnerability/CVE-2021-20197
Type: osv

## Details
There is an open race window when writing output in the following utilities in GNU binutils version 2.35 and earlier:ar, objcopy, strip, ranlib. When these utilities are run as a privileged user (presumably as part of a script updating binaries across different users), an unprivileged user can trick these utilities into getting ownership of arbitrary files through a symlink.

## References
- https://security.gentoo.org/glsa/202208-30
- https://security.netapp.com/advisory/ntap-20210528-0009/
- https://bugzilla.redhat.com/show_bug.cgi?id=1913743
- https://sourceware.org/bugzilla/show_bug.cgi?id=26945
