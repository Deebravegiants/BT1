# [M] CVE-2022-2905

## Summary
Severity: Medium
Advisory: CVE-2022-2905
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-09
Source: https://osv.dev/vulnerability/CVE-2022-2905
Type: osv

## Details
An out-of-bounds memory read flaw was found in the Linux kernel's BPF subsystem in how a user calls the bpf_tail_call function with a key larger than the max_entries of the map. This flaw allows a local user to gain unauthorized access to data.

## References
- https://lore.kernel.org/bpf/984b37f9fdf7ac36831d2137415a4a915744c1b6.1661462653.git.daniel%40iogearbox.net/
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2121800
