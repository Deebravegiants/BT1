# [M] CVE-2021-47152

## Summary
Severity: Medium
Advisory: CVE-2021-47152
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47152
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: fix data stream corruption

Maxim reported several issues when forcing a TCP transparent proxy
to use the MPTCP protocol for the inbound connections. He also
provided a clean reproducer.

The problem boils down to 'mptcp_frag_can_collapse_to()' assuming
that only MPTCP will use the given page_frag.

If others - e.g. the plain TCP protocol - allocate page fragments,
we can end-up re-using already allocated memory for mptcp_data_frag.

Fix the issue ensuring that the to-be-expanded data fragment is
located at the current page frag end.

v1 -> v2:
 - added missing fixes tag (Mat)

## References
- https://git.kernel.org/stable/c/18e7f0580da15cac1e79d73683ada5a9e70980f8
- https://git.kernel.org/stable/c/29249eac5225429b898f278230a6ca2baa1ae154
- https://git.kernel.org/stable/c/3267a061096efc91eda52c2a0c61ba76e46e4b34
