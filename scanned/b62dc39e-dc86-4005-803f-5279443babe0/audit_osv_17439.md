# [H] CVE-2020-15172

## Summary
Severity: High
Advisory: CVE-2020-15172
Aliases: GHSA-rm7m-j4xp-rv2p
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-15
Source: https://osv.dev/vulnerability/CVE-2020-15172
Type: osv

## Details
The Act module for Red Discord Bot before commit 6b9f3b86 is vulnerable to Remote Code Execution. With this exploit, Discord users can use specially crafted messages to perform destructive actions and/or access sensitive information. Unloading the Act module with `unload act` can render this exploit inaccessible.

## References
- https://github.com/zephyrkul/FluffyCogs/commit/6b9f3b862e1f0a5429c62f3090f814e53a242347
- https://github.com/zephyrkul/FluffyCogs/security/advisories/GHSA-rm7m-j4xp-rv2p
