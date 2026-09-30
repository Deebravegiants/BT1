# [H] High centralization risk in STBL_USST::bridgeBurn

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23366
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Current implementation of STBL_USST::bridgeBurn allows BRIDGE_ROLE to burn tokens from any arbitrary address without user approval. This creates unnecessary centralization risk when a safer approach is already demonstrated in the protocol's own STBL_Token contract.

```solidity
// STBL_USST.sol
function bridgeBurn(
    address _from, // @audit can be any address
    uint256 _amt,
    bytes memory _data
) external whenNotPaused onlyRole(BRIDGE_ROLE) {
    _burn(_from, _amt); // @audit Burns from arbitrary address without consent
    emit BridgeBurn(_from, _amt, _data);
}
```

The above approach allows the BRIDGE_ROLE (initialized to the DEFAULT_ADMIN) to burn tokens from any address.

An alternate implementation already implemented in STBL_TOKEN is much safer:

```solidity
// STBL_Token.sol
function bridgeBurn(uint256 _amt) external whenNotPaused onlyRole(BRIDGE_ROLE) {
    _burn(_msgSender(), _amt); // @audit Only burns caller's (bridge's) own tokens
}
```

## Recommendation
Consider using the STBL_Token code for implementing bridgeBurn functionality. Alternatively, first transfer tokens from the caller into the contract and then burn them.
