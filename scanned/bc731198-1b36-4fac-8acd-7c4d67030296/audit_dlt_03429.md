# [M] Missing calls to `_updateTokenInRegistry` leads to incorrect state of tokens in registry

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1404
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/CurveConnector.sol#L212
https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/MaverickConnector.sol#L137
https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/GearBoxV3.sol#L62
https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/MorphoBlueConnector.sol#L58
https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/PrismaConnector.sol#L75
https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/BalancerConnector.sol#L64


# Vulnerability details

## Impact
If the _updateTokenInRegistry() function is not called when it should be, the registry may not accurately reflect the current balances of tokens in the connectors leading to incorrect state.

## Proof of Concept
[_updateTokenInRegistry()](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/helpers/BaseConnector.sol#L135) is called in different connector contracts functions. The purpose of this function is to update the token registry to reflect the current balance of a specified token. It can add a new token to the registry or remove a token with zero balance.

```js
 function _updateTokenInRegistry(address token, bool remove) internal {
        (address accountingManager,) = registry.getVaultAddresses(vaultId);
        // the value function is inside the accounting manager contract (so we can use the accounting manager address as the calculator connector)
        bytes32 positionId = registry.calculatePositionId(accountingManager, 0, abi.encode(token));
        // if the token is not in the registry, we add it or remove it if the remove flag is true
        uint256 positionIndex =
            registry.getHoldingPositionIndex(vaultId, positionId, address(this), abi.encode(address(this)));
        if ((positionIndex == 0 && !remove) || (positionIndex > 0 && remove)) {
            emit UpdateTokenInRegistry(token, remove);
            registry.updateHoldingPosition(vaultId, positionId, abi.encode(address(this)), "", remove);
        }
    }
```

According to protocol docs:
  > This function is called to ensure the registry is accurate after liquidity is added, removed, or swaps are performed. It should reflect the current state of tokens held by this connector.

But such calls are MISSING in various functions of different connectors where liquidity is either added or removed. 


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1404_
