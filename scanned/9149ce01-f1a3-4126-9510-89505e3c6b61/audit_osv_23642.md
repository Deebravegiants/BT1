# [H] NFSD: prevent integer overflow on 32 bit systems

## Summary
Severity: High
Advisory: CVE-2022-49279
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49279
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: prevent integer overflow on 32 bit systems

On a 32 bit system, the "len * sizeof(*p)" operation can have an
integer overflow.

## References
- https://git.kernel.org/stable/c/23a9dbbe0faf124fc4c139615633b9d12a3a89ef
- https://git.kernel.org/stable/c/303cd6173dce0a28d26526c77814eb90a41bd898
- https://git.kernel.org/stable/c/3a2789e8ccb4a3e2a631f6817a2d3bb98b8c4fd8
- https://git.kernel.org/stable/c/79b1c54fc6ce09ee0d5fe088bb3de26ae2150e3c
- https://git.kernel.org/stable/c/7af164fa2f1abc577d357d22d83a2f3490875d7e
- https://git.kernel.org/stable/c/ce1aa09cc14ed625104acc2d487bd92b9a88efe2
- https://git.kernel.org/stable/c/e4195d27306ea468a6dc3a27af6f586709951229
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49279.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49279
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
