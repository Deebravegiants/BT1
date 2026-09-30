# [H] CVE-2020-14351

## Summary
Severity: High
Advisory: CVE-2020-14351
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-03
Source: https://osv.dev/vulnerability/CVE-2020-14351
Type: osv

## Details
A flaw was found in the Linux kernel. A use-after-free memory flaw was found in the perf subsystem allowing a local attacker with permission to monitor perf events to corrupt memory and possibly escalate privileges. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://lists.debian.org/debian-lts-announce/2020/12/msg00027.html
- https://lists.debian.org/debian-lts-announce/2020/12/msg00015.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1862849
