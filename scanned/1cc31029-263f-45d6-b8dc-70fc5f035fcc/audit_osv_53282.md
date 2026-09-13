# [H] CVE-2022-3623

## Summary
Severity: High
Advisory: CVE-2022-3623
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-20
Source: https://osv.dev/vulnerability/CVE-2022-3623
Type: osv

## Details
A vulnerability was found in Linux Kernel. It has been declared as problematic. Affected by this vulnerability is the function follow_page_pte of the file mm/gup.c of the component BPF. The manipulation leads to race condition. The attack can be launched remotely. It is recommended to apply a patch to fix this issue. The identifier VDB-211921 was assigned to this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00000.html
- https://vuldb.com/?id.211921
- https://www.debian.org/security/2023/dsa-5324
- https://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf-next.git/commit/?id=fac35ba763ed07ba93154c95ffc0c4a55023707f
