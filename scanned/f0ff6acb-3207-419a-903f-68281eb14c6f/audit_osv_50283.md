# [M] CVE-2020-10767

## Summary
Severity: Medium
Advisory: CVE-2020-10767
Aliases: A-156766097, ASB-A-156766097
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-09-15
Source: https://osv.dev/vulnerability/CVE-2020-10767
Type: osv

## Details
A flaw was found in the Linux kernel before 5.8-rc1 in the implementation of the Enhanced IBPB (Indirect Branch Prediction Barrier). The IBPB mitigation will be disabled when STIBP is not available or when the Enhanced Indirect Branch Restricted Speculation (IBRS) is available. This flaw allows a local attacker to perform a Spectre V2 style attack when this configuration is active. The highest threat from this vulnerability is to confidentiality.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10767
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=21998a351512eba4ed5969006f0c55882d995ada
