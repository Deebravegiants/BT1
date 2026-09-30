# [M] Loss of pending messages

## Summary
Severity: Medium
Contest weight: 0.5632
Dataset id: 1698
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
If there are any unprocessed messages to be executed or processed, while removeConnectedChain is called, then they may be stuck from getting processed on the other end. If these messages have transactions for any token transfer then it will get stuck or lost.
```

## Proof of Concept
```solidity
Contract : MessageProxy.sol Line : 313

function removeConnectedChain(string memory schainName) public virtual override onlyChainConnector {
    bytes32 schainHash = keccak256(abi.encodePacked(schainName));
    require(connectedChains[schainHash].inited, "Chain is not initialized");
    delete connectedChains[schainHash];
}
```

## Recommendation
Check if there are any pending or unprocessed messages while removeConnectedChain is called and revert in that case. Better to implement some functionality like pause just locally for the chain to be removed, before the actual removeConnectedChain is called.

It duplicates #57 

I don’t believe this to be a duplicate.

I think the finding is valid in that because of the synchronicity of broadcasting messages, the chain could be removed before it receives all messages.

This is a risk that end users do face when interacting with the system and the only use case I could think of would be for a malicious admin to deny certain operations.

That said I don’t believe there’s any easy solution as this would have to be addressed at the meta level.

I do think the finding is valid and of medium severity

cstrangedk (SKALE) commented: Issue is acknowledged and work is pending on the roadmap to prevent improper use of removeConnectedChain.
