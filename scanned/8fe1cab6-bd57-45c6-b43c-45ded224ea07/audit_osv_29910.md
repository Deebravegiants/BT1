# [H] bpf: Fix use-after-free in bpf_uprobe_multi_link_attach()

## Summary
Severity: High
Advisory: CVE-2024-47675
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47675
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix use-after-free in bpf_uprobe_multi_link_attach()

If bpf_link_prime() fails, bpf_uprobe_multi_link_attach() goes to the
error_free label and frees the array of bpf_uprobe's without calling
bpf_uprobe_unregister().

This leaks bpf_uprobe->uprobe and worse, this frees bpf_uprobe->consumer
without removing it from the uprobe->consumers list.

## References
- https://git.kernel.org/stable/c/5fe6e308abaea082c20fbf2aa5df8e14495622cf
- https://git.kernel.org/stable/c/790c630ab0e7d7aba6d186581d4627c09fce60f3
- https://git.kernel.org/stable/c/7c1d782e5afbf7c50ba74ecc4ddc18a05d63e5ee
- https://git.kernel.org/stable/c/cdf27834c3dd5d9abf7eb8e4ee87ee9e307eb25c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47675.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47675
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
