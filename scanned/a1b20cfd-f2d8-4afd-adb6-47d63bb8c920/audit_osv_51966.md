# [M] CVE-2021-46908

## Summary
Severity: Medium
Advisory: CVE-2021-46908
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46908
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Use correct permission flag for mixed signed bounds arithmetic

We forbid adding unknown scalars with mixed signed bounds due to the
spectre v1 masking mitigation. Hence this also needs bypass_spec_v1
flag instead of allow_ptr_leaks.

## References
- https://git.kernel.org/stable/c/4ccdc6c6cae38b91c871293fb0ed8c6845a61b51
- https://git.kernel.org/stable/c/4f3ff11204eac0ee23acf64deecb3bad7b0db0c6
- https://git.kernel.org/stable/c/9601148392520e2e134936e76788fc2a6371e7be
