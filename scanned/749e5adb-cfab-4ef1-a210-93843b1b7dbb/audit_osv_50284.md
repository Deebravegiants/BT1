# [M] CVE-2020-10768

## Summary
Severity: Medium
Advisory: CVE-2020-10768
Aliases: A-169505929, ASB-A-169505929
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-09-16
Source: https://osv.dev/vulnerability/CVE-2020-10768
Type: osv

## Details
A flaw was found in the Linux Kernel before 5.8-rc1 in the prctl() function, where it can be used to enable indirect branch speculation after it has been disabled. This call incorrectly reports it as being 'force disabled' when it is not and opens the system to Spectre v2 attacks. The highest threat from this vulnerability is to confidentiality.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10768
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=4d8df8cbb9156b0a0ab3f802b80cb5db57acc0bf
