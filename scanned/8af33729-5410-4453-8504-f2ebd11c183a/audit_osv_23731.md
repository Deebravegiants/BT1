# [M] RDMA/hfi1: Fix potential integer multiplication overflow errors

## Summary
Severity: Medium
Advisory: CVE-2022-49404
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49404
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/hfi1: Fix potential integer multiplication overflow errors

When multiplying of different types, an overflow is possible even when
storing the result in a larger type. This is because the conversion is
done after the multiplication. So arithmetic overflow and thus in
incorrect value is possible.

Correct an instance of this in the inter packet delay calculation.  Fix by
ensuring one of the operands is u64 which will promote the other to u64 as
well ensuring no overflow.

## References
- https://git.kernel.org/stable/c/06039d8afefdbac05bcea5f397188407eba2996d
- https://git.kernel.org/stable/c/252f4afd4557a2e7075f793a5c80fe6dd9e9ee4a
- https://git.kernel.org/stable/c/31dca00d0cc9f4133320d72eb7e3720badc6d6e6
- https://git.kernel.org/stable/c/3f09ec80f115d2875d747ed28adc1773037e0f8b
- https://git.kernel.org/stable/c/79c164e61f818054cd6012e9035701840d895c51
- https://git.kernel.org/stable/c/8858284dd74906fa00f04f0252c75df4893a7959
- https://git.kernel.org/stable/c/a89cb7ddf6a89bab6012e19da38b7cdb26175c19
- https://git.kernel.org/stable/c/ef5ab2e48a5f9960e2352332b7cdb7064bb49032
- https://git.kernel.org/stable/c/f93e91a0372c922c20d5bee260b0f43b4b8a1bee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49404.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49404
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
