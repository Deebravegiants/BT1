# [H] crypto: skcipher - Fix reqsize handling

## Summary
Severity: High
Advisory: CVE-2025-40182
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40182
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: skcipher - Fix reqsize handling

Commit afddce13ce81d ("crypto: api - Add reqsize to crypto_alg")
introduced cra_reqsize field in crypto_alg struct to replace type
specific reqsize fields. It looks like this was introduced specifically
for ahash and acomp from the commit description as subsequent commits
add necessary changes in these alg frameworks.

However, this is being recommended for use in all crypto algs [1]
instead of setting reqsize using crypto_*_set_reqsize(). Using
cra_reqsize in skcipher algorithms, hence, causes memory
corruptions and crashes as the underlying functions in the algorithm
framework have not been updated to set the reqsize properly from
cra_reqsize. [2]

Add proper set_reqsize calls in the skcipher init function to
properly initialize reqsize for these algorithms in the framework.

[1]: https://lore.kernel.org/linux-crypto/aCL8BxpHr5OpT04k@gondor.apana.org.au/
[2]: https://gist.github.com/Pratham-T/24247446f1faf4b7843e4014d5089f6b

## References
- https://git.kernel.org/stable/c/229c586b5e86979badb7cb0d38717b88a9e95ddd
- https://git.kernel.org/stable/c/f041339d6b9a5a46437f0c48fc7279c92af7a513
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40182.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40182
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
