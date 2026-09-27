# [M] Fusion by IPOR incident: Fusion has released a security update stating that its IPOR USDC Fusion Optimizer contains a vulnerability in the Arbitrum Vault

## Summary
Severity: Medium
Target: Fusion by IPOR
Loss: $ 336,000
Attack method: Smart Contract Vulnerability
Published: 2026-01-06
Source: https://x.com/ipor_io/status/2008728627190321480
Type: slowmist-incident

## Details
Fusion has released a security update stating that its IPOR USDC Fusion Optimizer contains a vulnerability in the Arbitrum Vault. The IPOR team was notified and confirmed on January 6 that the vulnerability had resulted in a loss of approximately $336,000 USDC. This exploit only affected a specific older version of the Fusion Vault, and due to its unique configuration, it was the only vault susceptible to this particular attack vector. According to further analysis by SlowMist, the root cause of the incident lies in the underlying contract delegated by the EOA account controlled via EIP‑7702, which contained a security flaw allowing arbitrary external calls. The attacker exploited this flaw to create and configure a malicious circuit-breaker contract targeting the Plasma Vault, thereby illicitly extracting funds from the vault. The official statement noted that the loss represents less than 1% of the total funds secured by Fusion. The team is currently working with Security Alliance to track the funds and attempt recovery. IPOR DAO will cover the deficit from its treasury, and all affected depositors will receive full compensation. Additionally, according to CertiK, approximately $267,000 of the stolen funds have been cross‑chain transferred to the Ethereum network and subsequently moved into Tornado Cash. On January 7, the IPOR team announced on X that the funds have been recovered, and a 10% bounty agreement has been reached with the white-hat party, which will be covered by the IPOR DAO. The incident has now been concluded as a good-faith white-hat security event.
