# [H] Admin can't burn tokens from blocklisted addresses because of a check in _beforeTokenTransfer 

## Summary
Severity: High
Chain: Smart contract
Component: 2023-09-ondo
Published: 2023-09-05
Source: https://github.com/code-423n4/2023-09-ondo-findings/issues/136
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-09-ondo/blob/main/contracts/usdy/rUSDY.sol#L642


# Vulnerability details

## Impact
The function `burn` is made so the admin can burn rUSDY tokens from ***any account*** - this is stated in the comments. However, the admin can't burn tokens if the account from which he's trying to burn tokens is blocklisted/sanctioned/not on the allowlist. 
## Proof of Concept
Let's check the `burn` function which calls the internal `_burnShares` function:
```javascript
function burn(
    address _account,
    uint256 _amount
  ) external onlyRole(BURNER_ROLE) {
    uint256 sharesAmount = getSharesByRUSDY(_amount);

    _burnShares(_account, sharesAmount);

    usdy.transfer(msg.sender, sharesAmount / BPS_DENOMINATOR);

    emit TokensBurnt(_account, _amount);
  }

  function _burnShares(
    address _account,
    uint256 _sharesAmount
  ) internal whenNotPaused returns (uint256) {
    require(_account != address(0), "BURN_FROM_THE_ZERO_ADDRESS");

    _beforeTokenTransfer(_account, address(0), _sharesAmount); <--

    uint256 accountShares = shares[_account];
    require(_sharesAmount <= accountShares, "BURN_AMOUNT_EXCEEDS_BALANCE");

    uint256 preRebaseTokenAmount = getRUSDYByShares(_sharesAmount);

```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-09-ondo-findings/issues/136_
