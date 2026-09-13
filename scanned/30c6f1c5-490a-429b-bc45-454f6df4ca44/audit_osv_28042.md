# [H] libbpf: Use OPTS_SET() macro in bpf_xdp_query()

## Summary
Severity: High
Advisory: CVE-2024-27050
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27050
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

libbpf: Use OPTS_SET() macro in bpf_xdp_query()

When the feature_flags and xdp_zc_max_segs fields were added to the libbpf
bpf_xdp_query_opts, the code writing them did not use the OPTS_SET() macro.
This causes libbpf to write to those fields unconditionally, which means
that programs compiled against an older version of libbpf (with a smaller
size of the bpf_xdp_query_opts struct) will have its stack corrupted by
libbpf writing out of bounds.

The patch adding the feature_flags field has an early bail out if the
feature_flags field is not part of the opts struct (via the OPTS_HAS)
macro, but the patch adding xdp_zc_max_segs does not. For consistency, this
fix just changes the assignments to both fields to use the OPTS_SET()
macro.

## References
- https://git.kernel.org/stable/c/682ddd62abd4bdcee7584246903e7a2df005fe0d
- https://git.kernel.org/stable/c/92a871ab9fa59a74d013bc04f321026a057618e7
- https://git.kernel.org/stable/c/cd3be9843247edb8fc6fcd8d8237cbce2bc19f5e
- https://git.kernel.org/stable/c/fa5bef5e80c6a3321b2b1a7070436f3bc5daf07c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27050.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27050
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
