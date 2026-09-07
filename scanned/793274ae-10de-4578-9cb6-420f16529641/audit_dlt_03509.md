# [M] Incorrect totalsupply value will be returned due to erroneous return data decode implementation

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-09-kakarot
Published: 2024-10-25
Source: https://github.com/code-423n4/2024-09-kakarot-findings/issues/32
Type: code-finding

## Details
# Lines of code

https://github.com/kkrt-labs/kakarot/blob/7411a5520e8a00be6f5243a50c160e66ad285563/solidity_contracts/src/CairoPrecompiles/DualVmToken.sol#L82


# Vulnerability details

## Proof of Concept
The returned value of `totalSupply()` in a starknet ERC20 contract is expected to fit in uint256, which is expressed in `(uint128, uint128)` with the first uint128 representing the lower 128bits. 

The issue is current implementation of DualVMToken::totalSupply incorrectly decode `returnData` as uint256 instead of `(uint128, uint128)`. Because the first uint128 is the lower 128bits of a uint256 number. This means, `totalSupply` will return an incorrect value because it only reads the lower 128bits. 
```solidity
//kakarot/solidity_contracts/lib/kakarot-lib/src/CairoLib.sol
    function totalSupply() external view returns (uint256) {
        bytes memory returnData = starknetToken.staticcallCairo("total_supply");
|>      return abi.decode(returnData, (uint256));
    }
```
(https://github.com/kkrt-labs/kakarot/blob/7411a5520e8a00be6f5243a50c160e66ad285563/solidity_contracts/src/CairoPrecompiles/DualVmToken.sol#L82)

Impacts: 
`totalSupply` will return incorrect value. Due to `totalSupply` is critical in many defi or accounting based logic, this potentially leads to fund loss and errorneas accounting in any user application that uses DualVMToken.sol. Depending on the context of the application that calls DualVMToken.sol, the fund loss could be critical.

## Recommended Mitigation Steps
In totalSupply(), change the decode following _balanceOf’s implementation:
```solidity
...
        (uint128 valueLow, uint128 valueHigh) = abi.decode(
            returnData,
            (uint128, uint128)
        );
        return uint256(valueLow) + (uint256(valueHigh) << 128);

```





_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-09-kakarot-findings/issues/32_
