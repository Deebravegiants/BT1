# [H] CVE-2017-1000405

## Summary
Severity: High
Advisory: CVE-2017-1000405
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-30
Source: https://osv.dev/vulnerability/CVE-2017-1000405
Type: osv

## Details
The Linux Kernel versions 2.6.38 through 4.14 have a problematic use of pmd_mkdirty() in the touch_pmd() function inside the THP implementation. touch_pmd() can be reached by get_user_pages(). In such case, the pmd will become dirty. This scenario breaks the new can_follow_write_pmd()'s logic - pmd can become dirty without going through a COW cycle. This bug is not as severe as the original "Dirty cow" because an ext4 file (or any other regular file) cannot be mapped using THP. Nevertheless, it does allow us to overwrite read-only huge pages. For example, the zero huge page and sealed shmem files can be overwritten (since their mapping can be populated using THP). Note that after the first write page-fault to the zero page, it will be replaced with a new fresh (and zeroed) thp.

## References
- https://source.android.com/security/bulletin/pixel/2018-02-01
- http://www.securityfocus.com/bid/102032
- http://www.securitytracker.com/id/1040020
- https://access.redhat.com/errata/RHSA-2018:0180
- https://www.exploit-db.com/exploits/43199/
- https://medium.com/bindecy/huge-dirty-cow-cve-2017-1000405-110eca132de0
