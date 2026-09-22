# [H] bpf: Add the missing BPF_LINK_TYPE invocation for sockmap

## Summary
Severity: High
Advisory: CVE-2024-50123
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50123
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Add the missing BPF_LINK_TYPE invocation for sockmap

There is an out-of-bounds read in bpf_link_show_fdinfo() for the sockmap
link fd. Fix it by adding the missing BPF_LINK_TYPE invocation for
sockmap link

Also add comments for bpf_link_type to prevent missing updates in the
future.

## References
- https://git.kernel.org/stable/c/6d79f12c0ce2bc8ff5f109093df1734bd6450615
- https://git.kernel.org/stable/c/c2f803052bc7a7feb2e03befccc8e49b6ff1f5f5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50123.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50123
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
