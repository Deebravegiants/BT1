# [C] crypto: aead - Fix reqsize handling

## Summary
Severity: Critical
Advisory: CVE-2025-68726
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68726
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.17.13, >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: aead - Fix reqsize handling

Commit afddce13ce81d ("crypto: api - Add reqsize to crypto_alg")
introduced cra_reqsize field in crypto_alg struct to replace type
specific reqsize fields. It looks like this was introduced specifically
for ahash and acomp from the commit description as subsequent commits
add necessary changes in these alg frameworks.

However, this is being recommended for use in all crypto algs
instead of setting reqsize using crypto_*_set_reqsize(). Using
cra_reqsize in aead algorithms, hence, causes memory corruptions and
crashes as the underlying functions in the algorithm framework have not
been updated to set the reqsize properly from cra_reqsize. [1]

Add proper set_reqsize calls in the aead init function to properly
initialize reqsize for these algorithms in the framework.

[1]: https://gist.github.com/Pratham-T/24247446f1faf4b7843e4014d5089f6b

## References
- https://git.kernel.org/stable/c/12b413f5460c393d1151a37f591140693eca0f84
- https://git.kernel.org/stable/c/64377e66e187164bd6737112d07257f5f0feb681
- https://git.kernel.org/stable/c/9b04d8f00569573796dd05397f5779135593eb24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68726.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68726
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
