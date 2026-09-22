# [M] SymCrypt SymCryptXmssSign function - Heap overflow via 64->32-bit leaf-count truncation

## Summary
Severity: Medium
Advisory: CVE-2026-35199
Aliases: GHSA-rvj8-8h6x-hjmg
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35199
Type: osv

## Details
SymCrypt is the core cryptographic function library currently used by Windows. From 103.5.0 to before 103.11.0, The SymCryptXmssSign function passes a 64-bit leaf count value to a helper function that accepts a 32-bit parameter. For XMSS^MT parameter sets with total tree height >= 32 (which includes standard predefined parameters), this causes silent truncation to zero, resulting in a drastically undersized scratch buffer allocation followed by a heap buffer overflow during signature computation. Exploiting this issue would require an application using SymCrypt to perform an XMSS^MT signature using an attacker-controlled parameter set. It is uncommon for applications to allow the use of attacker-controlled parameter sets for signing, since signing is a private key operation, and private keys must be trusted by definition. Additionally, XMSS(^MT) signing should only be performed in a Hardware Security Module (HSM). XMSS(^MT) signing is provided in SymCrypt only for testing purposes. This is a general rule irrespective of this CVE; XMSS(^MT) and other stateful signature schemes are only cryptographically secure when it is guaranteed that the same state cannot be reused for two different signatures, which cannot be guaranteed by software alone. For this reason, XMSS(^MT) signing is also not FIPS approved when performed outside of an HSM. Fixed in version 103.11.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35199.json
- https://github.com/microsoft/SymCrypt/security/advisories/GHSA-rvj8-8h6x-hjmg
- https://nvd.nist.gov/vuln/detail/CVE-2026-35199
