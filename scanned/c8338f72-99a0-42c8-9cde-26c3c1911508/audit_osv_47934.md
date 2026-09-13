# [M] CVE-2017-15127

## Summary
Severity: Medium
Advisory: CVE-2017-15127
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-14
Source: https://osv.dev/vulnerability/CVE-2017-15127
Type: osv

## Details
A flaw was found in the hugetlb_mcopy_atomic_pte function in mm/hugetlb.c in the Linux kernel before 4.13. A superfluous implicit page unlock for VM_SHARED hugetlbfs mapping could trigger a local denial of service (BUG).

## References
- http://www.securityfocus.com/bid/102517
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2018:1062
- https://access.redhat.com/security/cve/CVE-2017-15127
- https://bugzilla.redhat.com/show_bug.cgi?id=1525218
- https://github.com/torvalds/linux/commit/5af10dfd0afc559bb4b0f7e3e8227a1578333995
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=5af10dfd0afc559bb4b0f7e3e8227a1578333995
