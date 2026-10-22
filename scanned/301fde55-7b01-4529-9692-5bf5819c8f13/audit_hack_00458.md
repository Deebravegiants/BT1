# [H] Ekubo Protocol incident: According to Blockaid, Ekubo Protocol’s custom extension contract on Ethereum was attacked in the early hours, resulting in a loss

## Summary
Severity: High
Target: Ekubo Protocol
Loss: $ 1,400,000
Attack method: Smart Contract Vulnerability
Published: 2026-05-05
Source: https://x.com/blockaid_/status/2051757787714118125
Type: slowmist-incident

## Details
According to Blockaid, Ekubo Protocol’s custom extension contract on Ethereum was attacked in the early hours, resulting in a loss of approximately $1.4 million. Ekubo users themselves were not directly affected. Only users who had previously approved the V2 contract as a token spender were exposed to risk. The root cause lies in the IPayer.pay callback function within the Ekubo extension contract. Specifically, the payer, token, and amount parameters in the token.transferFrom call were directly sourced from the lock payload and could be fully controlled by the attacker. The contract failed to verify whether the payer was the initiator of the lock or an authorized payment source. As a result, the attacker was able to exploit prior ERC-20 approvals granted by users to the contract. By routing through the Core locking mechanism into the extension contract, the attacker could designate any previously approved user as the payer while setting themselves as the recipient, thereby draining user funds.
