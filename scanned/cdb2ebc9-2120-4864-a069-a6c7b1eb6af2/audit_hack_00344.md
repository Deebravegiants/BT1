# [M] Enjin incident: Enjin’s legacy ERC-1155 Crypto Items platform on Ethereum was exploited. The attacker used a storage-layout mismatch in delegate-c

## Summary
Severity: Medium
Target: Enjin
Loss: $ 162,000
Attack method: Smart Contract Vulnerability
Published: 2026-08-25
Source: https://x.com/SlowMist_Team/status/2092455321654694355
Type: slowmist-incident

## Details
Enjin’s legacy ERC-1155 Crypto Items platform on Ethereum was exploited. The attacker used a storage-layout mismatch in delegate-call adapters plus an unprotected initialize function to take over the Managed Delegate Proxy via DELEGATECALL. After gaining manager privileges, they registered a malicious adapter, transferred NFTs from about 52 wallets without approval, and melted them to redeem the backing ENJ from the reserve, draining approximately 5.24 million ENJ .
