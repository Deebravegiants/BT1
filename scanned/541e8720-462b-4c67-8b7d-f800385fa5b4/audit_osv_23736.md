# [H] tracing: Fix potential double free in create_var_ref()

## Summary
Severity: High
Advisory: CVE-2022-49410
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49410
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing: Fix potential double free in create_var_ref()

In create_var_ref(), init_var_ref() is called to initialize the fields
of variable ref_field, which is allocated in the previous function call
to create_hist_field(). Function init_var_ref() allocates the
corresponding fields such as ref_field->system, but frees these fields
when the function encounters an error. The caller later calls
destroy_hist_field() to conduct error handling, which frees the fields
and the variable itself. This results in double free of the fields which
are already freed in the previous function.

Fix this by storing NULL to the corresponding fields when they are freed
in init_var_ref().

## References
- https://git.kernel.org/stable/c/058cb6d86b9789377216c936506b346aaa1eb581
- https://git.kernel.org/stable/c/37443b3508b8cce6832f8d25cb4550b2f7801f50
- https://git.kernel.org/stable/c/4fdfb15e08598711dbf50daf56a33965232daf0e
- https://git.kernel.org/stable/c/99696a2592bca641eb88cc9a80c90e591afebd0f
- https://git.kernel.org/stable/c/bd83ff3bbfb003832481c9bff999d12385f396ae
- https://git.kernel.org/stable/c/c27f744ceefadc7bbeb14233b6abc150ced617d2
- https://git.kernel.org/stable/c/f8b383f83cb573152c577eca1ef101e89995b72a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49410.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49410
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
