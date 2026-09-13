# [H] CVE-2018-10675

## Summary
Severity: High
Advisory: CVE-2018-10675
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-02
Source: https://osv.dev/vulnerability/CVE-2018-10675
Type: osv

## Details
The do_get_mempolicy function in mm/mempolicy.c in the Linux kernel before 4.12.9 allows local users to cause a denial of service (use-after-free) or possibly have unspecified other impact via crafted system calls.

## References
- https://access.redhat.com/errata/RHSA-2018:3590
- https://access.redhat.com/errata/RHSA-2018:2164
- https://access.redhat.com/errata/RHSA-2018:2384
- https://access.redhat.com/errata/RHSA-2018:3586
- http://www.securityfocus.com/bid/104093
- https://access.redhat.com/errata/RHSA-2018:2785
- https://access.redhat.com/errata/RHSA-2018:2924
- https://access.redhat.com/errata/RHSA-2018:2933
- https://help.ecostruxureit.com/display/public/UADCE725/Security+fixes+in+StruxureWare+Data+Center+Expert+v7.6.0
- https://access.redhat.com/errata/RHSA-2018:2395
- https://access.redhat.com/errata/RHSA-2018:2791
- https://access.redhat.com/errata/RHSA-2018:2925
- https://access.redhat.com/errata/RHSA-2018:3540
- https://usn.ubuntu.com/3754-1/
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.12.9
- https://github.com/torvalds/linux/commit/73223e4e2e3867ebf033a5a8eb2e5df0158ccc99
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=73223e4e2e3867ebf033a5a8eb2e5df0158ccc99
