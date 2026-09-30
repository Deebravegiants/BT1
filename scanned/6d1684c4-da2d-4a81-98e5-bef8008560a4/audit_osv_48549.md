# [M] CVE-2017-9211

## Summary
Severity: Medium
Advisory: CVE-2017-9211
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-23
Source: https://osv.dev/vulnerability/CVE-2017-9211
Type: osv

## Details
The crypto_skcipher_init_tfm function in crypto/skcipher.c in the Linux kernel through 4.11.2 relies on a setkey function that lacks a key-size check, which allows local users to cause a denial of service (NULL pointer dereference) via a crafted application.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9933e113c2e87a9f46a40fde8dafbf801dca1ab9
- https://github.com/torvalds/linux/commit/9933e113c2e87a9f46a40fde8dafbf801dca1ab9
- https://patchwork.kernel.org/patch/9718933/
