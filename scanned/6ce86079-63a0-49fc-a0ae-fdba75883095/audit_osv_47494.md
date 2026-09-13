# [M] CVE-2016-7042

## Summary
Severity: Medium
Advisory: CVE-2016-7042
CVSS: 6.2 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-16
Source: https://osv.dev/vulnerability/CVE-2016-7042
Type: osv

## Details
The proc_keys_show function in security/keys/proc.c in the Linux kernel through 4.8.2, when the GNU Compiler Collection (gcc) stack protector is enabled, uses an incorrect buffer size for certain timeout data, which allows local users to cause a denial of service (stack memory corruption and panic) by reading the /proc/keys file.

## References
- http://www.securityfocus.com/bid/93544
- https://source.android.com/security/bulletin/2017-01-01.html
- http://rhn.redhat.com/errata/RHSA-2017-0817.html
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- https://access.redhat.com/errata/RHSA-2017:2669
- https://bugzilla.redhat.com/show_bug.cgi?id=1373966
- http://www.openwall.com/lists/oss-security/2016/10/13/5
