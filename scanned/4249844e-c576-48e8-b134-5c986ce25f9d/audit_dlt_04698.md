# [M] Lack of the validation whether `tokenID` inputted is valid or not

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-frankendao
Published: 2022-11-16
Source: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/46
Type: sherlock-finding

## Details
0xmuxyz

medium

# Lack of the validation whether `tokenID` inputted is valid or not

## Summary
- Lack of the validation whether `tokenID` inputted is valid or not

## Vulnerability Detail
- On the assumption is that, the range of tokenID of FrankenPunks and FrankenMonsters are defined like below:
  - **_FrankenPunk token IDs_** begin at `0` and continue through `9,999` . 
  - **_FrankenMonster token IDs_** begin at `10,000` and continue through `20,010` . 

- However, there is no validation check in `stake()` function in the Staking.sol whether each `tokenID` inputted is a valid tokenID or not. (Please see the "Code Snippet" of this issue below)
   - And the access control modifier of `stake()` function is `"public"` . Therefore, any external users can call `stake()` function and inputs arbitrary `tokenID` into the `_tokenIds` parameters of `stake()` function. 
   - As a result, the transaction could be fail if an external malicious user inputs tokenID that is `more than 20,011` into the `_tokenIds` parameters of `stake()` function, this transaction could be fail.

## Impact
For example,
- If an external malicious user inputs `tokenID=20,011`(or inputs tokenID that is `more than 20,011` ) into the `_tokenIds` parameters of `stake()` function, this transaction could be fail.

## Code Snippet
- There is no validation check in the `stake()` function in the Staking.sol whether each `tokenID` inputted is a valid tokenID or not.
   - And the access control modifier of `stake()` function is `"public"` . Therefore, any external users can call `stake()` function and inputs arbitrary `tokenID` into the `_tokenIds` parameters of `stake()` function. 
      https://github.com/sherlock-audit/2022-11-frankendao/blob/main/src/Staking.sol#L341-L351
```solidity
  function stake(uint[] calldata _tokenIds, uint _unlockTime) public {
    // Refunds gas if stakingRefund is true and hasn't been used by this user in the past 24 hours
    if (stakingRefund && lastStakingRefund[msg.sender] + refundCooldown <= block.timestamp) {
      uint256 startGas = gasleft();
      _stake(_tokenIds, _unlockTime);
      lastStakingRefund[msg.sender] = block.timestamp;
      _refundGas(startGas);
    } else {
      _stake(_tokenIds, _unlockTime);
    }
  }
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/46_
