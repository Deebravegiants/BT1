# [H] CVE-2023-4147

## Summary
Severity: High
Advisory: CVE-2023-4147
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-07
Source: https://osv.dev/vulnerability/CVE-2023-4147
Type: osv

## Details
A use-after-free flaw was found in the Linux kernel’s Netfilter functionality when adding a rule with NFTA_RULE_CHAIN_ID. This flaw allows a local user to crash or escalate their privileges on the system.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://www.debian.org/security/2023/dsa-5480
- https://www.debian.org/security/2023/dsa-5492
- https://access.redhat.com/errata/RHSA-2023:5069
- https://access.redhat.com/errata/RHSA-2023:5093
- https://access.redhat.com/errata/RHSA-2023:7411
- https://security.netapp.com/advisory/ntap-20231020-0006/
- https://access.redhat.com/errata/RHSA-2023:5091
- https://access.redhat.com/errata/RHSA-2023:7382
- https://access.redhat.com/errata/RHSA-2023:7389
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=0ebc1064e4874d5987722a2ddbc18f94aa53b211
- https://www.spinics.net/lists/stable/msg671573.html
- https://access.redhat.com/security/cve/CVE-2023-4147
- https://bugzilla.redhat.com/show_bug.cgi?id=2225239
