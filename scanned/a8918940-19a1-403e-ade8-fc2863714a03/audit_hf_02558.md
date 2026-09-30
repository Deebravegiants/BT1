# [M] ParametersandReturnValuesMismatchinContractsandInter- faces

## Summary
Severity: Medium
Contest weight: 0.5933
Dataset id: 13705
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• There is a mismatch between contract and interface function return values. In contract PortalV2MultiAsset:

```solidity
function getUpdateAccount(address _user, uint256 _amount, bool
_isPositiveAmount) public view returns (
uint256 lastUpdateTime,
uint256 lastMaxLockDuration,
uint256 stakedBalance,
uint256 maxStakeDebt,
uint256 portalEnergy,
uint256 availableToWithdraw,
uint256 portalEnergyTokensRequired
)
```

In interface IPortalV2MultiAsset:

```solidity
function getUpdateAccount(address _user, uint256 _amount, bool
_isPositiveAmount) external view returns (
address user,
uint256 lastUpdateTime,
uint256 lastMaxLockDuration,
uint256 stakedBalance,
uint256 maxStakeDebt,
uint256 portalEnergy,
uint256 availableToWithdraw
);
```

• There is a mismatch between contracts and interfaces function parameters and return values. In contract AdapterV1:

```solidity
function getUpdateAccount(
    address _user,
    uint256 _amount,
    bool _isPositiveAmount
) public view returns (
    uint256 lastUpdateTime,
    uint256 lastMaxLockDuration,
    uint256 stakedBalance,
    uint256 maxStakeDebt,
    uint256 portalEnergy,
    uint256 availableToWithdraw,
    uint256 portalEnergyTokensRequired
)

function stake(uint256 _amount) external payable notMigrating
nonReentrant

function addLiquidity(SwapData memory _swap) internal
```

In interface IAdapterV1:

```solidity
function getUpdateAccount(
    address _user,
    uint256 _amount
) external view returns (address, uint256, uint256, uint256, uint256, uint256, uint256);

function stake(
    address _receiver,
    uint256 _amount
) external;

function addLiquidity(
    address _receiver,
    uint256 amountPSMDesired,
    uint256 amountWETHDesired,
    uint256 amountPSMMin,
    uint256 amountWETHMin,
    uint256 _deadline
) external returns (uint256 amountPSM, uint256 amountWETH, uint256 liquidity);
```

Even though the contract PortalV2MultiAsset itself isn’t within the scope of this audit, the interface IPortalV2MultiAsset reveals a mismatch between return values. This mismatch between parameters and return values can potentially lead to unexpected errors since anyone who uses these interfaces will expect to receive and provide different values.

## Recommendation
Apply the necessary changes in the mentioned interfaces so that definitions and implementations fully match.
