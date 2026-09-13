# [H] s390/bpf: Zero-extend bpf prog return values and kfunc arguments

## Summary
Severity: High
Advisory: CVE-2026-53110
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53110
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/bpf: Zero-extend bpf prog return values and kfunc arguments

s390x ABI requires callers to zero-extend unsigned arguments and
sign-extend signed arguments, and callees to zero-extend unsigned
return values and sign-extend signed return values.

s390 BPF JIT currently implements only sign extension. Fix this
omission and implement zero extension too.

## References
- https://git.kernel.org/stable/c/202e42e4aa890172366354b233c42c73107a3f59
- https://git.kernel.org/stable/c/366b0e05ee24f5ba62bdc7ec1346038258b9a797
- https://git.kernel.org/stable/c/44c4f999b03f55debb1a0c5ab5c1796895a1adf8
- https://git.kernel.org/stable/c/834918a77be51419383bf1dda9f02b81ecf26b34
- https://git.kernel.org/stable/c/edc90a12073b9a530064a99945c183dde120cb99
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53110.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53110
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
