# [H] CVE-2018-14634

## Summary
Severity: High
Advisory: CVE-2018-14634
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-25
Source: https://osv.dev/vulnerability/CVE-2018-14634
Type: osv

## Details
An integer overflow flaw was found in the Linux kernel's create_elf_tables() function. An unprivileged local user with access to SUID (or otherwise privileged) binary could use this flaw to escalate their privileges on the system. Kernel versions 2.6.x, 3.10.x and 4.14.x are believed to be vulnerable.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2018-14634
- http://www.openwall.com/lists/oss-security/2021/07/20/2
- https://access.redhat.com/errata/RHSA-2018:2924
- https://access.redhat.com/errata/RHSA-2018:3586
- https://access.redhat.com/errata/RHSA-2018:3590
- https://usn.ubuntu.com/3775-2/
- http://www.securityfocus.com/bid/105407
- https://access.redhat.com/errata/RHSA-2018:2763
- https://access.redhat.com/errata/RHSA-2018:3540
- https://access.redhat.com/errata/RHSA-2018:3591
- https://access.redhat.com/errata/RHSA-2018:2846
- https://support.f5.com/csp/article/K20934447?utm_source=f5support&amp%3Butm_medium=RSS
- https://usn.ubuntu.com/3775-1/
- https://access.redhat.com/errata/RHSA-2018:2748
- https://access.redhat.com/errata/RHSA-2018:2925
- https://access.redhat.com/errata/RHSA-2018:2933
- https://access.redhat.com/errata/RHSA-2018:3643
- https://security.paloaltonetworks.com/CVE-2018-14634
- https://usn.ubuntu.com/3779-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14634
