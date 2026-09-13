# [M] CVE-2019-9857

## Summary
Severity: Medium
Advisory: CVE-2019-9857
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2019-9857
Type: osv

## Details
In the Linux kernel through 5.0.2, the function inotify_update_existing_watch() in fs/notify/inotify/inotify_user.c neglects to call fsnotify_put_mark() with IN_MASK_CREATE after fsnotify_find_mark(), which will cause a memory leak (aka refcount leak). Finally, this will cause a denial of service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NXLZ2V2ES37A3J7DMK4MZYIWV2LEZFLM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PPH3B7FJOMWD5JWUPZKB6T44KNT4PX2L/
- http://www.securityfocus.com/bid/107527
- https://security.netapp.com/advisory/ntap-20190404-0002/
- https://git.kernel.org/pub/scm/linux/kernel/git/jack/linux-fs.git/commit/?h=fsnotify&id=62c9d2674b31d4c8a674bee86b7edc6da2803aea
- https://patchwork.kernel.org/patch/10836283/
