# [M] Bypass of mintingAllowance in mint()

## Summary
Severity: Medium
Contest weight: 0.4543
Dataset id: 13380
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The StakedTokenV1 contract provides an interface, i.e., mint(), for the minters to mint new wBETH tokens to themselves. Each minter has a minting allowance (mintingAllowance) conﬁgured by Binance, which indicates how many tokens that minter is allowed to issue. While reviewing the implementation of the mint() routine, we notice the minter can issue more tokens than his/her minting allowance. To elaborate, we show below the code snippet of the _mint() routine, which is called from the mint() routine to mint new wBETH tokens to the minter. As we can see from the comment of the _mint() routine (lines 280-281), the amount of tokens to mint must be less than or equal to the minting allowance of the caller. However, the implementation does not properly validate the input amount with the mintingAllowance. As a result, the minter can mint more tokens than he/she is allowed to. Based on this, we suggest to validate the input amount with the minting allowance, and subtract the input amount from the minting allowance accordingly in the mint() routine.

```solidity
/**
 * @dev Function to mint tokens
 * @param _to The address that will receive the minted tokens.
 * @param _amount The amount of tokens to mint. Must be less than or equal
 * to the minterAllowance of the caller.
 * @return A boolean that indicates if the operation was successful.
 */
function _mint(address _to, uint256 _amount) internal
    whenNotPaused
    notBlacklisted(msg.sender)
    notBlacklisted(_to)
    returns (bool) {
    require(_to != address(0), "StakedTokenV1: mint to the zero address");
    require(_amount > 0, "StakedTokenV1: mint amount not greater than 0");
    totalSupply_ = totalSupply_.add(_amount);
    balances[_to] = balances[_to].add(_amount);
    emit Mint(msg.sender, _to, _amount);
    emit Transfer(address(0), _to, _amount);
    return true;
}
```

## Recommendation
Revisit the mint() routine to properly validate the input amount with the minting allowance, and subtract the input amount from the minting allowance accordingly.
