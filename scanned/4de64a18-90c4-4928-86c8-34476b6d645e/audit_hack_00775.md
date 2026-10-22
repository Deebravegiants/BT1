# [M] dYdX incident: On July 23, the dydx.exchange domain was discovered to have been compromised. The attacker changed the DNS Nameservers from Cloudf

## Summary
Severity: Medium
Target: dYdX
Loss: $ 31,000
Attack method: DNS Attack
Published: 2024-07-23
Source: https://dydx.exchange/blog/dns-nameserver-hijacking-postmortem
Type: slowmist-incident

## Details
On July 23, the dydx.exchange domain was discovered to have been compromised. The attacker changed the DNS Nameservers from Cloudflare to DDoS-Guard. The attacker also successfully removed the DNSSEC settings on the domain. The attacker hosted a malicious site which requested that any connected wallets transfer ETH and other ERC20 tokens to the attacker’s Ethereum address. Two users were affected, resulting in a loss of approximately $31,000.
