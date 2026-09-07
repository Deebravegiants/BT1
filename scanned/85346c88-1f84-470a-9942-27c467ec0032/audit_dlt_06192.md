# [M] Contract initialization is unprotected and is vulnerable to front-running

## Summary
Severity: Medium
Chain: Smart contract
Component: Smooth
Published: 2023-10-27
Source: https://github.com/hats-finance/Smooth-0x64bc275b37e62eec81a00ecaecd2b9567058f990/issues/1
Type: hats-finding

## Details
**Github username:** @0xfuje
**Submission hash (on-chain):** 0x2b440f1884c88f8ca016bc058bc3cf6d07f58a0152b675f34384192a5c9f3b66
**Severity:** medium

**Description:**
## Impact
Contract have to be redeployed with a fix. Funds can be lost if an attacker's initialization remains undetected

## Description
`DappnodeSmoothingPool` implements openzeppelin's upgradeable model. The problem is that it's unprotected from an attacker initializing the contract. The uninitialized contract can be taken over by the attacker for example by front-running the original deployer `intialize()` call. This applies to both the proxy and its implementation contract. 

From [openzeppelin's documentation](https://docs.openzeppelin.com/upgrades-plugins/1.x/writing-upgradeable#initializing_the_implementation_contract):
>Do not leave an implementation contract uninitialized. An uninitialized implementation contract can be taken over by an attacker, which may impact the proxy. To prevent the implementation contract from being used, you should invoke the  `_disableInitializers`  function in the constructor to automatically lock it when it is deployed

`DappNodeSmoothingPool.sol` - [`initialize()`](https://github.com/dappnode/mev-sp-contracts/blob/main/contracts/DappnodeSmoothingPool.sol#L182-L220)
```solidity
    function initialize(
        address _governance,
        uint256 _subscriptionCollateral,
        uint256 _poolFee,
        address _poolFeeRecipient,
        uint64 _checkpointSlotSize,
        uint64 _quorum
    ) external initializer {
        // Initialize requires
        require(
            _poolFee <= 10000,
            "DappnodeSmoothingPool::initialize: Pool fee cannot be greater than 100%"
        );

        require(
            _quorum != 0,
            "DappnodeSmoothingPool::initialize: Quorum cannot be 0"
        );

        // Set initialize parameters
        governance = _governance;
        subscriptionCollateral = _subscriptionCollateral;
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Smooth-0x64bc275b37e62eec81a00ecaecd2b9567058f990/issues/1_
