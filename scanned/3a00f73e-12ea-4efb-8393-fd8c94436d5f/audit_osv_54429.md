# [H] CVE-2023-6200

## Summary
Severity: High
Advisory: CVE-2023-6200
CVSS: 7.5 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-28
Source: https://osv.dev/vulnerability/CVE-2023-6200
Type: osv

## Details
A race condition was found in the Linux Kernel. Under certain conditions, an unauthenticated attacker from an adjacent network could send an ICMPv6 router advertisement packet, causing arbitrary code execution.

## References
- https://access.redhat.com/security/cve/CVE-2023-6200
- https://bugzilla.redhat.com/show_bug.cgi?id=2250377
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=dade3f6a1e4e
