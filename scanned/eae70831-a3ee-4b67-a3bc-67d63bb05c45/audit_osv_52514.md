# [M] CVE-2021-47529

## Summary
Severity: Medium
Advisory: CVE-2021-47529
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47529
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

iwlwifi: Fix memory leaks in error handling path

Should an error occur (invalid TLV len or memory allocation failure), the
memory already allocated in 'reduce_power_data' should be freed before
returning, otherwise it is leaking.

## References
- https://git.kernel.org/stable/c/4768935c25403ba96e7a745645df24a51a774b7e
- https://git.kernel.org/stable/c/a571bc28326d9f3e13f5f2d9cda2883e0631b0ce
