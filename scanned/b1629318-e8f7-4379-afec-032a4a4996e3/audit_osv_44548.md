# [M] phpseclib — non-constant-time X25519 scalar multiplication permits full private-key recovery

## Summary
Severity: Medium
Advisory: CVE-2026-84308
Aliases: GHSA-q97c-8qh3-fpc6
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84308
Type: osv

## Details
phpseclib is a PHP secure communications library. Prior to 3.0.57 and 4.0.1, pure-PHP X25519 scalar multiplication in phpseclib/Math/PrimeField/Integer.php performs data-dependent conditional modular reductions in add() and subtract(). During the Montgomery ladder in phpseclib/Crypt/EC/BaseCurves/Montgomery.php, the reduction behavior of each step depends on the secret scalar prefix, creating per-step timing and libgmp call-count observations that can reveal a reused 251-bit clamped private scalar. The phpseclib/Crypt/EC/Formats/Keys/MontgomeryPrivate.php derivation path invokes the pure-PHP multiplication without a native-engine check, while phpseclib/Crypt/EC/Formats/Keys/PKCS8.php reaches it when ext-sodium is unavailable. Exploitation requires a reused or long-lived X25519 private key, knowledge of the corresponding public key, execution of the pure-PHP path, and a local observer capable of resolving individual ladder steps or libgmp entry-point calls. Ephemeral X25519 keys, including phpseclib's normal SSH exchange path, are not affected. Recovery of the scalar permanently compromises operations that reuse that key. This issue is fixed in versions 3.0.57 and 4.0.1.

## References
- https://github.com/phpseclib/phpseclib/releases/tag/3.0.57
- https://github.com/phpseclib/phpseclib/releases/tag/4.0.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84308.json
- https://github.com/phpseclib/phpseclib/security/advisories/GHSA-q97c-8qh3-fpc6
- https://nvd.nist.gov/vuln/detail/CVE-2026-84308
- https://github.com/phpseclib/phpseclib/commit/fb56bc5bb9009b54a6c26b31aeec8ed944f17373
