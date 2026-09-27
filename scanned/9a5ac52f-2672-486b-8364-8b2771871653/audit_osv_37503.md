# [H] crypto: tegra - Add missing CRYPTO_ALG_ASYNC

## Summary
Severity: High
Advisory: CVE-2026-31739
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31739
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: tegra - Add missing CRYPTO_ALG_ASYNC

The tegra crypto driver failed to set the CRYPTO_ALG_ASYNC on its
asynchronous algorithms, causing the crypto API to select them for users
that request only synchronous algorithms.  This causes crashes (at
least).  Fix this by adding the flag like what the other drivers do.
Also remove the unnecessary CRYPTO_ALG_TYPE_* flags, since those just
get ignored and overridden by the registration function anyway.

## References
- https://git.kernel.org/stable/c/3aea268b6d5cde3b087df9eeecc3bc620aa09513
- https://git.kernel.org/stable/c/429d05565eb19ee545d8a8395991372adbe4daf3
- https://git.kernel.org/stable/c/4b56770d345524fc2acc143a2b85539cf7d74bc1
- https://git.kernel.org/stable/c/bdbf027a4504b4a86740de6beb6d18a957331839
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31739.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31739
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
