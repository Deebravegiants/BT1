# [H] Incomplete TVL Calculation in `AerodromeConnector::_getPositionTVL` Function.

## Summary
Severity: High
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1360
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/AerodromeConnector.sol#L125-L134


# Vulnerability details

## Impact

The [AerodromeConnector::stake](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/AerodromeConnector.sol#L100) function allows to stake liquidity tokens to the gauge pool. However, the [AerodromeConnector::_getPositionTVL](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/AerodromeConnector.sol#L125) function, which is responsible for calculating the Total Value Locked (TVL), does not take into account the liquidity tokens deposited in the gauge pool. This oversight will result in an incorrect calculation of the TVL, which could negatively impact the overall functionality of the protocol that utilizes the TVL metric.

## Proof of Concept

The [AerodromeConnector::stake](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/AerodromeConnector.sol#L100) function allows to deposit and stake liquidity tokens in the gauge pool.

```solidity
AerodromeConnector.sol
100: function stake(address pool, uint256 liquidity) public onlyManager nonReentrant {
101:         address gauge = voter.gauges(pool);
102:         IERC20(pool).forceApprove(address(gauge), liquidity);
103:         IGauge(gauge).deposit(liquidity, address(this));  // @audit-info this sends tokens to the gauge
104:     }
```

The implementation of the [Gauge::deposit](https://github.com/aerodrome-finance/contracts/blob/b934e7ae398ea6c251a4d5af2119776c06f1f23d/contracts/gauges/Gauge.sol#L151) is as follows:

```solidity
    function deposit(uint256 _amount, address _recipient) external {
        _depositFor(_amount, _recipient);
    }

    function _depositFor(uint256 _amount, address _recipient) internal nonReentrant {
        if (_amount == 0) revert ZeroAmount();
        if (!IVoter(voter).isAlive(address(this))) revert NotAlive();


        address sender = _msgSender();
        _updateRewards(_recipient);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1360_
