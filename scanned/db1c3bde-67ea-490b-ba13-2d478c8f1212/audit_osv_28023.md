# [H] userfaultfd: change src_folio after ensuring it's unpinned in UFFDIO_MOVE

## Summary
Severity: High
Advisory: CVE-2024-27007
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27007
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.8.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

userfaultfd: change src_folio after ensuring it's unpinned in UFFDIO_MOVE

Commit d7a08838ab74 ("mm: userfaultfd: fix unexpected change to src_folio
when UFFDIO_MOVE fails") moved the src_folio->{mapping, index} changing to
after clearing the page-table and ensuring that it's not pinned.  This
avoids failure of swapout+migration and possibly memory corruption.

However, the commit missed fixing it in the huge-page case.

## References
- https://git.kernel.org/stable/c/c0205eaf3af9f5db14d4b5ee4abacf4a583c3c50
- https://git.kernel.org/stable/c/df5f6e683e7f21a15d8be6e7a0c7a46436963ebe
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4EZ6PJW7VOZ224TD7N4JZNU6KV32ZJ53/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DAMSOZXJEPUOXW33WZYWCVAY7Z5S7OOY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GCBZZEC7L7KTWWAS2NLJK6SO3IZIL4WW/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27007.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27007
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
