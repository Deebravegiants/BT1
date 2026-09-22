# [H] crypto: algif_hash - Remove bogus SGL free on zero-length error path

## Summary
Severity: High
Advisory: CVE-2024-26824
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26824
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: algif_hash - Remove bogus SGL free on zero-length error path

When a zero-length message is hashed by algif_hash, and an error
is triggered, it tries to free an SG list that was never allocated
in the first place.  Fix this by not freeing the SG list on the
zero-length error path.

## References
- https://git.kernel.org/stable/c/24c890dd712f6345e382256cae8c97abb0406b70
- https://git.kernel.org/stable/c/775f3c1882a493168e08fdb8cde0865c8f3a8a29
- https://git.kernel.org/stable/c/9c82920359b7c1eddaf72069bcfe0ffddf088cd0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26824.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26824
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
