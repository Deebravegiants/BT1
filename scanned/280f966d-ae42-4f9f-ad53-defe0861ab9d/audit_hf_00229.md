# [M] _totalSupply not updated in _transferMint

## Summary
Severity: Medium
Contest weight: 0.5797
Dataset id: 1174
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The functions `_transferMint()` and `_transferBurn()` of OverlayToken.sol don’t update `_totalSupply`. Whereas the similar functions `_mint()` and `_burn()` do update `_totalSupply`.

This means that `_totalSupply` and `totalSupply()` will not show a realistic view of the total OVL tokens.

For the protocol itself it isn’t such a problem because this value isn’t used in the protocol (as far as I can see). But other protocols building on Overlay may use it, as well as user interfaces and analytic platforms.

## Proof of Concept
```solidity
function _mint(address account, uint256 amount) internal virtual {
    ...
    _totalSupply += amount;
}
```

```solidity
function _burn(address account, uint256 amount) internal virtual {
    ...
    _totalSupply -= amount;
}
```

Recommended Mitigation Steps

Update `_totalSupply` in `_transferMint()` and `_transferBurn()`

> We’re not sure if this is a 1 or a 2. Definitely, at least a one - this is an incorrect implementation of the spec. 
> 
> But is it a two? It wouldn’t lose funds with our contracts, we make no use of the total supply of OVL in our accounting.
> 
> This might prove to be a vulnerability if another protocol, like Ribbon, used us for a vault of theirs, made use of total supply, and failed to discern this problem.

## Recommendation
No recommendation
