# [M] Vault can be DoS

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-05-bakerfi
Published: 2024-06-01
Source: https://github.com/code-423n4/2024-05-bakerfi-findings/issues/37
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-05-bakerfi/blob/59b1f70cbf170871f9604e73e7fe70b70981ab43/contracts/libraries/RebaseLibrary.sol#L32


# Vulnerability details

## Impact
When totalSupply = 0, the attacker donates 1wei token, causing the number of shares to remain 0 at deposit time.


## Proof of Concept

The `toBase` function only determines whether `total.elastic(_totalAssets)` is 0, not whether `totalSupply` is 0.

```solidity
    function toBase(Rebase memory total, uint256 elastic,bool roundUp
    ) internal pure returns (uint256 base) {
@       if (total.elastic == 0) {
            base = elastic;
        } else {
            //total.base = totalSupply ; total.elastic = _totalAssets
            base = (elastic * total.base) / total.elastic;
            if (roundUp && (base * total.elastic) / total.base < elastic) {
                base++;
            }
        }
    }
```

When totalSupply=0, if _totalAssets > 0, `toBase` always returns 0.

An attacker can make a donation of _totalAssets > 0, the `toBase` function will then compute base through a branch in the else statement, since totalSupply=0
base = 0 * elastic / total.elastic = 0,

As a result, the number of deposit shares is always 0, and the protocol will not work.

```solidity
    function deposit(address receiver) ....{
        .....
        shares = total.toBase(amount, false);
        _mint(receiver, shares);
        emit Deposit(msg.sender, receiver, msg.value, shares);
    }
```

An attacker can send Collateral token to the `StrategyAAVEv3(address(this))` contract,

_totalAssets = collateralBalance - debtBalance

```solidity
    function _getMMPosition() internal virtual override view returns ( uint256 collateralBalance, uint256 debtBalance ) {
        DataTypes.ReserveData memory wethReserve = (aaveV3().getReserveData(wETHA()));
        DataTypes.ReserveData memory colleteralReserve = (aaveV3().getReserveData(ierc20A()));
        debtBalance = IERC20(wethReserve.variableDebtTokenAddress).balanceOf(address(this));
        collateralBalance = IERC20(colleteralReserve.aTokenAddress).balanceOf(address(this));
    }
```

## Tools Used
vscode, manual

## Recommended Mitigation Steps
```diff
    function toBase(Rebase memory total, uint256 elastic,bool roundUp
    ) internal pure returns (uint256 base) {
-        if (total.elastic == 0) {
+        if (total.elastic == 0 || total.base == 0) {
            base = elastic;
        } else {
            //total.base = totalSupply ; total.elastic = _totalAssets
            base = (elastic * total.base) / total.elastic;
            if (roundUp && (base * total.elastic) / total.base < elastic) {
                base++;
            }
        }
    }
```





## Assessed type

DoS
