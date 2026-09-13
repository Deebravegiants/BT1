# [M] CVE-2021-28971

## Summary
Severity: Medium
Advisory: CVE-2021-28971
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-22
Source: https://osv.dev/vulnerability/CVE-2021-28971
Type: osv

## Details
In intel_pmu_drain_pebs_nhm in arch/x86/events/intel/ds.c in the Linux kernel through 5.11.8 on some Haswell CPUs, userspace applications (such as perf-fuzzer) can cause a system crash because the PEBS status in a PEBS record is mishandled, aka CID-d88d05a9e0b6.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4VCKIOXCOZGXBEZMO5LGGV5MWCHO6FT3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PTRNPQTZ4GVS46SZ4OBXY5YDOGVPSTGQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T2S3I4SLRNRUQDOFYUS6IUAZMQNMPNLG/
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- https://security.netapp.com/advisory/ntap-20210430-0003/
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=d88d05a9e0b6d9356e97129d4ff9942d765f46ea
