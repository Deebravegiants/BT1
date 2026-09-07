# [H] Bit flip attack vulnerability in cookie-encrypter

## Summary
Severity: High
Advisory: GHSA-h63v-hw6g-x8hp
CVE: CVE-2024-53441
CWE: CWE-325, CWE-327
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-12-09
Source: https://github.com/advisories/GHSA-h63v-hw6g-x8hp
Type: github-advisory

## Affected
- npm: `cookie-encrypter` — affected >=0

## Details
due to a weakness in the encryption method used in cookie-encrypter an attack can use the world visible IV to edit encrypted cookies without decrypting the cookie itself. This is known as an AES CBC bit flipping attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53441
- https://github.com/ebourmalo/cookie-encrypter/issues/9
- https://crypto.stackexchange.com/questions/66085/bit-flipping-attack-on-cbc-mode
- https://gist.github.com/mathysEthical/f45f1503f87381090e38a33c50eec971
- https://github.com/ebourmalo/cookie-encrypter
- https://mathys.reboux.pro/CVE/2024/53441
