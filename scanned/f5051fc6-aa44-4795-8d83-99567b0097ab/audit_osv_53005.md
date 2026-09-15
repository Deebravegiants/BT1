# [H] CVE-2022-2590

## Summary
Severity: High
Advisory: CVE-2022-2590
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-31
Source: https://osv.dev/vulnerability/CVE-2022-2590
Type: osv

## Details
A race condition was found in the way the Linux kernel's memory subsystem handled the copy-on-write (COW) breakage of private read-only shared memory mappings. This flaw allows an unprivileged, local user to gain write access to read-only memory mappings, increasing their privileges on the system.

## References
- https://lore.kernel.org/linux-mm/20220808073232.8808-1-david%40redhat.com/
- https://www.openwall.com/lists/oss-security/2022/08/08/1
