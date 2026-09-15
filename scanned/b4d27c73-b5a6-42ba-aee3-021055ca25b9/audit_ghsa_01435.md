# [C] Undefined Behavior in zencashjs

## Summary
Severity: Critical
Advisory: GHSA-xfrc-7mj2-5xh9
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-xfrc-7mj2-5xh9
Type: github-advisory

## Affected
- npm: `zencashjs` — affected >=0 <1.2.0

## Details
Versions of `zencashjs` prior to 1.2.0 may cause loss of funds when used with cryptocurrency wallets. The package relies on a string comparison of the first two characters of a Horizen address to determine the destination address type of a transaction (P2PKH or P2SH). Due to the base58 address prefixes chosen in Horizen there exists the possibility of a clash of address prefixes for testnet P2PKH and mainnet P2SH addresses, testnet P2PKH addresses start with “zt” while a subset of mainnet P2SH addresses can also start with “zt”. The package interprets transactions sent to a “zt” P2SH address on mainnet as P2PKH transactions erroneously. Any funds sent to a mainnet P2SH multisignature address starting with “zt” will be sent to the wrong address and be lost.


## Recommendation

Upgrade to version 1.2.0 or later.

## References
- https://github.com/ZencashOfficial/zencashjs/commit/db01bd94b9f8a956d7835e934500eaa643f8bd13#diff-42d8d2088a96641b563b25ad908b0c0fR146
- https://www.npmjs.com/advisories/1035
