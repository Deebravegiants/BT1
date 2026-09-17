# [C] CVE-2019-18814

## Summary
Severity: Critical
Advisory: CVE-2019-18814
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-07
Source: https://osv.dev/vulnerability/CVE-2019-18814
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.3.9. There is a use-after-free when aa_label_parse() fails in aa_audit_rule_init() in security/apparmor/audit.c.

## References
- https://lists.debian.org/debian-lts-announce/2020/08/msg00019.html
- https://support.f5.com/csp/article/K21561554?utm_source=f5support&amp%3Butm_medium=RSS
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://lore.kernel.org/patchwork/patch/1142523/
