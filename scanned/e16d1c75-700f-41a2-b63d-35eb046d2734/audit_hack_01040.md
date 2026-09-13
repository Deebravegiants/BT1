# [M] Klever incident: Klever published a report on an external security incident on July 12. All wallets affected by the suspicious activity on July 12

## Summary
Severity: Medium
Target: Klever
Loss: -
Attack method: Low Entropy Mnemonic Vulnerability
Published: 2023-07-12
Source: https://klever.org/en/blog/klever-alert-external-security-incident
Type: slowmist-incident

## Details
Klever published a report on an external security incident on July 12. All wallets affected by the suspicious activity on July 12 were reported to be affected by a known vulnerability caused by low-entropy mnemonics. It's important to underscore that this issue is not exclusive to Klever. Reports indicate that users of multiple wallet providers are affected. All the wallets involved were imported into Klever Wallet K5. These wallets had not been originally created using Klever Wallet K5, instead all the wallets were created using an old and weak pseudorandom number generator (PRNG) algorithm as their entropy source. This algorithm was commonly used in early versions of various cryptocurrency wallet providers, which relied on the Javascript platform. The use of such a weak PRNG algorithm can significantly compromise the security and unpredictability of the generated keys, potentially making them more vulnerable to attacks or unauthorized access. Klever strongly recommends immediately migrating old wallets to new wallets created on Klever Wallet K5 or Klever Safe.
