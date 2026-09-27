# [M] CVE-2021-26933

## Summary
Severity: Medium
Advisory: CVE-2021-26933
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-02-17
Source: https://osv.dev/vulnerability/CVE-2021-26933
Type: osv

## Details
An issue was discovered in Xen 4.9 through 4.14.x. On Arm, a guest is allowed to control whether memory accesses are bypassing the cache. This means that Xen needs to ensure that all writes (such as the ones during scrubbing) have reached the memory before handing over the page to a guest. Unfortunately, the operation to clean the cache is happening before checking if the page was scrubbed. Therefore there is no guarantee when all the writes will reach the memory.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4GELN5E6MDR5KQBJF5M5COUUED3YFZTD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EOAJBVAVR6RSCUCHNXPVSNRPSFM7INMP/
- https://www.debian.org/security/2021/dsa-4888
- http://xenbits.xen.org/xsa/advisory-364.html
