# [M] CVE-2021-47122

## Summary
Severity: Medium
Advisory: CVE-2021-47122
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-15
Source: https://osv.dev/vulnerability/CVE-2021-47122
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: caif: fix memory leak in caif_device_notify

In case of caif_enroll_dev() fail, allocated
link_support won't be assigned to the corresponding
structure. So simply free allocated pointer in case
of error

## References
- https://git.kernel.org/stable/c/9348c1f10932f13b299cbc8b1bd5f780751fae49
- https://git.kernel.org/stable/c/af2806345a37313f01b1c9f15e046745b8ee2daa
- https://git.kernel.org/stable/c/b042e2b2039565eb8f0eb51c14fbe1ef463c8cd8
- https://git.kernel.org/stable/c/b53558a950a89824938e9811eddfc8efcd94e1bb
- https://git.kernel.org/stable/c/f52f4fd67264c70cd0b4ba326962ebe12d9cba94
- https://git.kernel.org/stable/c/3be863c11cab725add9fef4237ed4e232c3fc3bb
- https://git.kernel.org/stable/c/4bca2034b41c15b62d47a19158bb76235fd4455d
- https://git.kernel.org/stable/c/6a0e317f61094d377335547e015dd2ff12caf893
