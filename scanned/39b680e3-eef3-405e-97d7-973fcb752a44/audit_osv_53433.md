# [H] CVE-2022-42332

## Summary
Severity: High
Advisory: CVE-2022-42332
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-21
Source: https://osv.dev/vulnerability/CVE-2022-42332
Type: osv

## Details
x86 shadow plus log-dirty mode use-after-free In environments where host assisted address translation is necessary but Hardware Assisted Paging (HAP) is unavailable, Xen will run guests in so called shadow mode. Shadow mode maintains a pool of memory used for both shadow page tables as well as auxiliary data structures. To migrate or snapshot guests, Xen additionally runs them in so called log-dirty mode. The data structures needed by the log-dirty tracking are part of aformentioned auxiliary data. In order to keep error handling efforts within reasonable bounds, for operations which may require memory allocations shadow mode logic ensures up front that enough memory is available for the worst case requirements. Unfortunately, while page table memory is properly accounted for on the code path requiring the potential establishing of new shadows, demands by the log-dirty infrastructure were not taken into consideration. As a result, just established shadow page tables could be freed again immediately, while other code is still accessing them on the assumption that they would remain allocated.

## References
- http://www.openwall.com/lists/oss-security/2023/03/21/1
- http://xenbits.xen.org/xsa/advisory-427.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5L6PM4RE7MUE6OWA32ZVOXCP235RM2TM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/APBMS2Q6746AXAFAITNJMGBNFGNMVLWR/
- https://security.gentoo.org/glsa/202402-07
- https://www.debian.org/security/2023/dsa-5378
- https://xenbits.xenproject.org/xsa/advisory-427.txt
