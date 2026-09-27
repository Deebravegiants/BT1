# [M] CVE-2022-0264

## Summary
Severity: Medium
Advisory: CVE-2022-0264
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-02-04
Source: https://osv.dev/vulnerability/CVE-2022-0264
Type: osv

## Details
A vulnerability was found in the Linux kernel's eBPF verifier when handling internal data structures. Internal memory locations could be returned to userspace. A local attacker with the permissions to insert eBPF code to the kernel can use this to leak internal kernel memory details defeating some of the exploit mitigations in place for the kernel. This flaws affects kernel versions < v5.16-rc6

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2041547
