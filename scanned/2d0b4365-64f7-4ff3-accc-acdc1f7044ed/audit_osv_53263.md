# [H] CVE-2022-3534

## Summary
Severity: High
Advisory: CVE-2022-3534
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-17
Source: https://osv.dev/vulnerability/CVE-2022-3534
Type: osv

## Details
A vulnerability classified as critical has been found in Linux Kernel. Affected is the function btf_dump_name_dups of the file tools/lib/bpf/btf_dump.c of the component libbpf. The manipulation leads to use after free. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-211032.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf-next.git/commit/?id=93c660ca40b5d2f7c1b1626e955a8e9fa30e0749
- https://vuldb.com/?id.211032
- https://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf-next.git/commit/?id=93c660ca40b5d2f7c1b1626e955a8e9fa30e0749
- https://vuldb.com/?id.211032
