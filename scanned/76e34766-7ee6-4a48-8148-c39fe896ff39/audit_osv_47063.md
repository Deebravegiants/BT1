# [M] CVE-2015-8844

## Summary
Severity: Medium
Advisory: CVE-2015-8844
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2015-8844
Type: osv

## Details
The signal implementation in the Linux kernel before 4.3.5 on powerpc platforms does not check for an MSR with both the S and T bits set, which allows local users to cause a denial of service (TM Bad Thing exception and panic) via a crafted application.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=d2b9d2a5ad5ef04ff978c9923d19730cb05efd55
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://rhn.redhat.com/errata/RHSA-2016-2584.html
- https://github.com/torvalds/linux/commit/d2b9d2a5ad5ef04ff978c9923d19730cb05efd55
- https://bugzilla.redhat.com/show_bug.cgi?id=1326540
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.3.5
- http://www.openwall.com/lists/oss-security/2016/04/13/1
- http://www.securitytracker.com/id/1035594
