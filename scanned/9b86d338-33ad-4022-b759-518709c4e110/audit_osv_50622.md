# [M] CVE-2020-25704

## Summary
Severity: Medium
Advisory: CVE-2020-25704
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-02
Source: https://osv.dev/vulnerability/CVE-2020-25704
Type: osv

## Details
A flaw memory leak in the Linux kernel performance monitoring subsystem was found in the way if using PERF_EVENT_IOC_SET_FILTER. A local user could use this flaw to starve the resources causing denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2020/12/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/12/msg00027.html
- https://www.starwindsoftware.com/security/sw-20220802-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=1895961
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=7bdb157cdebbf95a1cd94ed2e01b338714075d00
- https://www.openwall.com/lists/oss-security/2020/11/09/1
