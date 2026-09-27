# [M] CVE-2021-3611

## Summary
Severity: Medium
Advisory: CVE-2021-3611
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-05-11
Source: https://osv.dev/vulnerability/CVE-2021-3611
Type: osv

## Details
A stack overflow vulnerability was found in the Intel HD Audio device (intel-hda) of QEMU. A malicious guest could use this flaw to crash the QEMU process on the host, resulting in a denial of service condition. The highest threat from this vulnerability is to system availability. This flaw affects QEMU versions prior to 7.0.0.

## References
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20220624-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=1973784
- https://gitlab.com/qemu-project/qemu/-/issues/542
