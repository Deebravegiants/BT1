# [M] CVE-2020-10766

## Summary
Severity: Medium
Advisory: CVE-2020-10766
Aliases: A-169505740, ASB-A-169505740
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-09-15
Source: https://osv.dev/vulnerability/CVE-2020-10766
Type: osv

## Details
A logic bug flaw was found in Linux kernel before 5.8-rc1 in the implementation of SSBD. A bug in the logic handling allows an attacker with a local account to disable SSBD protection during a context switch when additional speculative execution mitigations are in place. This issue was introduced when the per task/process conditional STIPB switching was added on top of the existing SSBD switching. The highest threat from this vulnerability is to confidentiality.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10766
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=dbbe2ad02e9df26e372f38cc3e70dab9222c832e
