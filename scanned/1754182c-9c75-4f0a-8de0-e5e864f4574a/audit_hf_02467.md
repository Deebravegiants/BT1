# [M] MINTER _BURNER_ ROLE can burn any amount of Yieldy from an arbitrary address

## Summary
Severity: Medium
Contest weight: 0.3738
Dataset id: 13224
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Using the `burn()` function of `Yieldy`, an address with `MINTER_BURNER_ROLE` can burn an arbitrary amount of tokens from any address.

We believe this is unnecessary and poses a serious centralization risk.

A malicious or compromised `MINTER_BURNER_ROLE` address can take advantage of this.

## Recommendation
Consider removing the `MINTER_BURNER_ROLE` and change `burn()` function to:
```solidity
function burn(uint256 _amount) external override 
{
    _burn(_msgSender(), _amount);
}
```

There’s tons of centralization risks already, this is acknowledged, but for yieldies to work, there needs to be a trusted party.

Leaving as medium - the code can be upgraded but the code is being assessed as is.
