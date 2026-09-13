# [H] xen-netfront: Add missing skb_mark_for_recycle

## Summary
Severity: High
Advisory: CVE-2024-27393
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-27393
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.15.154, >=5.16.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

xen-netfront: Add missing skb_mark_for_recycle

Notice that skb_mark_for_recycle() is introduced later than fixes tag in
commit 6a5bcd84e886 ("page_pool: Allow drivers to hint on SKB recycling").

It is believed that fixes tag were missing a call to page_pool_release_page()
between v5.9 to v5.14, after which is should have used skb_mark_for_recycle().
Since v6.6 the call page_pool_release_page() were removed (in
commit 535b9c61bdef ("net: page_pool: hide page_pool_release_page()")
and remaining callers converted (in commit 6bfef2ec0172 ("Merge branch
'net-page_pool-remove-page_pool_release_page'")).

This leak became visible in v6.8 via commit dba1b8a7ab68 ("mm/page_pool: catch
page_pool memory leaks").

## References
- http://www.openwall.com/lists/oss-security/2024/05/08/4
- https://git.kernel.org/stable/c/037965402a010898d34f4e35327d22c0a95cd51f
- https://git.kernel.org/stable/c/27aa3e4b3088426b7e34584274ad45b5afaf7629
- https://git.kernel.org/stable/c/4143b9479caa29bb2380f3620dcbe16ea84eb3b1
- https://git.kernel.org/stable/c/7c1250796b6c262b505a46192f4716b8c6a6a8c6
- https://git.kernel.org/stable/c/c8b7b2f158d9d4fb89cd2f68244af154f7549bb4
- http://xenbits.xen.org/xsa/advisory-457.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27393.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27393
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
