# [M] CVE-2022-4543

## Summary
Severity: Medium
Advisory: CVE-2022-4543
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-01-11
Source: https://osv.dev/vulnerability/CVE-2022-4543
Type: osv

## Details
A flaw named "EntryBleed" was found in the Linux Kernel Page Table Isolation (KPTI). This issue could allow a local attacker to leak KASLR base via prefetch side-channels based on TLB timing for Intel systems.

## References
- https://www.openwall.com/lists/oss-security/2022/12/16/3
- https://www.willsroot.io/2022/12/entrybleed.html
- https://www.openwall.com/lists/oss-security/2022/12/16/3
- https://www.openwall.com/lists/oss-security/2022/12/16/3
- https://www.willsroot.io/2022/12/entrybleed.html
