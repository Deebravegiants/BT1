# [M] CVE-2018-8087

## Summary
Severity: Medium
Advisory: CVE-2018-8087
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-13
Source: https://osv.dev/vulnerability/CVE-2018-8087
Type: osv

## Details
Memory leak in the hwsim_new_radio_nl function in drivers/net/wireless/mac80211_hwsim.c in the Linux kernel through 4.15.9 allows local users to cause a denial of service (memory consumption) by triggering an out-of-array error case.

## References
- https://access.redhat.com/errata/RHSA-2019:2029
- https://usn.ubuntu.com/3676-1/
- https://usn.ubuntu.com/3677-1/
- https://usn.ubuntu.com/3678-3/
- https://usn.ubuntu.com/3678-4/
- http://www.securityfocus.com/bid/103397
- https://access.redhat.com/errata/RHSA-2019:2043
- https://usn.ubuntu.com/3676-2/
- https://usn.ubuntu.com/3677-2/
- https://usn.ubuntu.com/3678-1/
- https://usn.ubuntu.com/3678-2/
- https://www.debian.org/security/2018/dsa-4188
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=0ddcff49b672239dda94d70d0fcf50317a9f4b51
- https://github.com/torvalds/linux/commit/0ddcff49b672239dda94d70d0fcf50317a9f4b51
