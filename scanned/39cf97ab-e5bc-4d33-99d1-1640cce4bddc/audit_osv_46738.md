# [H] CVE-2014-9940

## Summary
Severity: High
Advisory: CVE-2014-9940
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-05-02
Source: https://osv.dev/vulnerability/CVE-2014-9940
Type: osv

## Details
The regulator_ena_gpio_free function in drivers/regulator/core.c in the Linux kernel before 3.19 allows local users to gain privileges or cause a denial of service (use-after-free) via a crafted application.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=60a2362f769cf549dc466134efe71c8bf9fbaaba
- http://www.debian.org/security/2017/dsa-3945
- http://www.securityfocus.com/bid/98195
- https://github.com/torvalds/linux/commit/60a2362f769cf549dc466134efe71c8bf9fbaaba
- https://source.android.com/security/bulletin/2017-05-01
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=60a2362f769cf549dc466134efe71c8bf9fbaaba
- https://github.com/torvalds/linux/commit/60a2362f769cf549dc466134efe71c8bf9fbaaba
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=60a2362f769cf549dc466134efe71c8bf9fbaaba
- https://github.com/torvalds/linux/commit/60a2362f769cf549dc466134efe71c8bf9fbaaba
