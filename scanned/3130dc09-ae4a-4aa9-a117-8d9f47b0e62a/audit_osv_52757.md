# [H] CVE-2022-1048

## Summary
Severity: High
Advisory: CVE-2022-1048
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-29
Source: https://osv.dev/vulnerability/CVE-2022-1048
Type: osv

## Details
A use-after-free flaw was found in the Linux kernel’s sound subsystem in the way a user triggers concurrent calls of PCM hw_params. The hw_free ioctls or similar race condition happens inside ALSA PCM for other ioctls. This flaw allows a local user to crash or potentially escalate their privileges on the system.

## References
- https://security.netapp.com/advisory/ntap-20220629-0001/
- https://www.debian.org/security/2022/dsa-5127
- https://www.debian.org/security/2022/dsa-5173
- https://bugzilla.redhat.com/show_bug.cgi?id=2066706
- https://lore.kernel.org/lkml/20220322170720.3529-5-tiwai%40suse.de/T/#m1d3b791b815556012c6be92f1c4a7086b854f7f3
