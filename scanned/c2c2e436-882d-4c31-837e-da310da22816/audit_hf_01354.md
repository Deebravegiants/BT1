# [M] Extra checks in _verifySender() of GnosisBase

## Summary
Severity: Medium
Contest weight: 0.4201
Dataset id: 6830
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
According to the Gnosis bridge documentation the source chain id should also be checked using messageSourceChainId(). This is because in the future the same arbitrary message bridge contract could handle requests from different chains.
If a malicious actor would be able to have access to the contract at mirrorConnector on a to-be-supported chain that is not the MIRROR_DOMAIN, they can send an arbitrary root to this mainnet/L1 hub connector which the connector would mark it as coming from the MIRROR_DOMAIN. So the attacker can spoof/forge function calls and asset transfers by creating a payload root and using this along with their access to mirrorConnector on chain to send a cross-chain processMessage to the Gnosis hub connector and after they can use their payload root and proofs to forge/spoof transfers on the L1 chain.
Although it is unlikely that any other party could add a contract with the same address as _amb on another chain, it is safer to add additional checks.

```solidity
function _verifySender(address _amb, address _expected) internal view returns (bool) {
    require(msg.sender == _amb, "!bridge");
    return GnosisAmb(_amb).messageSender() == _expected;
}
```

## Recommendation
In function _verifySender() add a check to verify messageSourceChainId() == MIRROR_DOMAIN. Note: this will probably require adding an extra parameter to _verifySender().
