# [H] Missing bounds check on weight values in WeightedTokensVPCalc and WeightedVaultsVPCalc

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23365
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The WeightedTokensVPCalc and WeightedVaultsVPCalc contracts lack proper bounds checking when setting weight values, which could lead to integer overflow during voting power calculations or complete elimination of voting power through zero weights.  

The weight‑setting functions in both contracts accept any `uint208` value without validation:  

```solidity
// WeightedTokensVPCalc.sol
function setTokenWeight(address token, uint208 weight) public virtual checkPermission {
    _setTokenWeight(token, weight); // No bounds checking
}

// WeightedVaultsVPCalc.sol
function setVaultWeight(address vault, uint208 weight) public virtual checkPermission {
    _setVaultWeight(vault, weight); // No bounds checking
}
```  

The voting power calculation multiplies stake amounts by these weights without overflow protection:  

```solidity
// WeightedTokensVPCalc.sol
function stakeToVotingPower(address vault, uint256 stake, bytes memory extraData)
    public view virtual override returns (uint256) {
    return super.stakeToVotingPower(vault, stake, extraData) * getTokenWeight(_getCollateral(vault));
    //@audit could go to 0 or overflow based on weight set,!
}
```  

Impact: Cause an integer overflow (extremely large weight) or total domination of one token over the rest or complete voting power elimination (0 weight). While the weight‑setting functions are protected by the `checkPermission` modifier and controlled by network governance in production deployments, technical safeguards remain important.

## Recommendation
Consider implementing a min and max weight that are either constants or immutable.  

```solidity
contract WeightedTokensVPCalc is NormalizedTokenDecimalsVPCalc, PermissionManager {
    uint208 public constant MIN_WEIGHT = 1e6; // Minimum non-zero weight
    uint208 public constant MAX_WEIGHT = 1e18; // Maximum reasonable weight

    function setTokenWeight(address token, uint208 weight) public virtual checkPermission {
        require(weight <= MAX_WEIGHT, "Weight exceeds maximum");
        require(weight <= MAX_SAFE_WEIGHT, "Weight risks overflow");
        _setTokenWeight(token, weight);
    }
}
```
