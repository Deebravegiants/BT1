# [H] CVE-2019-11811

## Summary
Severity: High
Advisory: CVE-2019-11811
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-07
Source: https://osv.dev/vulnerability/CVE-2019-11811
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.0.4. There is a use-after-free upon attempted read access to /proc/ioports after the ipmi_si module is removed, related to drivers/char/ipmi/ipmi_si_intf.c, drivers/char/ipmi/ipmi_si_mem_io.c, and drivers/char/ipmi/ipmi_si_port_io.c.

## References
- https://access.redhat.com/errata/RHSA-2019:1873
- https://access.redhat.com/errata/RHSA-2019:1971
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.4
- https://security.netapp.com/advisory/ntap-20190719-0003/
- https://support.f5.com/csp/article/K01512680
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00071.html
- http://www.securityfocus.com/bid/108410
- https://access.redhat.com/errata/RHSA-2019:1891
- https://access.redhat.com/errata/RHSA-2019:1959
- https://access.redhat.com/errata/RHSA-2019:4057
- https://access.redhat.com/errata/RHSA-2019:4058
- https://access.redhat.com/errata/RHSA-2020:0036
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=401e7e88d4ef80188ffa07095ac00456f901b8c4
- https://github.com/torvalds/linux/commit/401e7e88d4ef80188ffa07095ac00456f901b8c4
