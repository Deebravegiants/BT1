# [M] CVE-2021-4145

## Summary
Severity: Medium
Advisory: CVE-2021-4145
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-01-25
Source: https://osv.dev/vulnerability/CVE-2021-4145
Type: osv

## Details
A NULL pointer dereference issue was found in the block mirror layer of QEMU in versions prior to 6.2.0. The `self` pointer is dereferenced in mirror_wait_on_conflicts() without ensuring that it's not NULL. A malicious unprivileged user within the guest could use this flaw to crash the QEMU process on the host when writing data reaches the threshold of mirroring node.

## References
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20220311-0004/
- https://bugzilla.redhat.com/show_bug.cgi?id=2034602
- https://gitlab.com/qemu-project/qemu/-/commit/66fed30c9cd11854fc878a4eceb507e915d7c9cd
