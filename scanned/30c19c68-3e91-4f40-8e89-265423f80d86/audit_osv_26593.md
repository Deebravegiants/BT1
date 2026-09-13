# [M] md/raid10: fix null-ptr-deref of mreplace in raid10_sync_request

## Summary
Severity: Medium
Advisory: CVE-2023-53380
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53380
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.251, >=5.5.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/raid10: fix null-ptr-deref of mreplace in raid10_sync_request

There are two check of 'mreplace' in raid10_sync_request(). In the first
check, 'need_replace' will be set and 'mreplace' will be used later if
no-Faulty 'mreplace' exists, In the second check, 'mreplace' will be
set to NULL if it is Faulty, but 'need_replace' will not be changed
accordingly. null-ptr-deref occurs if Faulty is set between two check.

Fix it by merging two checks into one. And replace 'need_replace' with
'mreplace' because their values are always the same.

## References
- https://git.kernel.org/stable/c/144c7fd008e0072b0b565f1157eec618de54ca8a
- https://git.kernel.org/stable/c/222cc459d59857ee28a5366dc225ab42b22f9272
- https://git.kernel.org/stable/c/2990e2ece18dd4cca71b3109c80517ad94adb065
- https://git.kernel.org/stable/c/34817a2441747b48e444cb0e05d84e14bc9443da
- https://git.kernel.org/stable/c/45fa023b3334a7ae6f6c4eb977295804222dfa28
- https://git.kernel.org/stable/c/b5015b97adda6a24dd3e713c63e521ecbeff25c6
- https://git.kernel.org/stable/c/f4368a462b1f9a8ecc2fdb09a28c3d4cad302a4f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53380.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53380
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
