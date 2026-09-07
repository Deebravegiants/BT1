# [M] hardcoding aave pool address is a serious aave integration flaw because valid pool addresses can change

## Summary
Severity: Medium
Chain: Smart contract
Component: Origami
Published: 2024-03-05
Source: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/58
Type: hats-finding

## Details
**Github username:** @adeolu98
**Twitter username:** 0x29f
**Submission hash (on-chain):** 0x9d2f9d0e58f1570994fbaa5bad4af878bafeda065dc074b07fb0c6a6e8f1a8a6
**Severity:** medium

**Description:**
**Description**\
The `OrigamiAaveV3FlashLoanProvider` contract is a  "A permisionless flashloan wrapper over an Aave/Spark flashloan pool". The contract stores the address of the AAVE pool in an immutable variable, essentially hardcoding the address. This is not advised by the aave protocol according to their docs.

**Attack Scenario**\
 - `OrigamiAaveV3FlashLoanProvider` is deployed and AAVE pool address is set in constructor to be immutable as seen [here](https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/blob/185a93e25071b6a110ca190e94a6a826e982b2d6/apps/protocol/contracts/common/flashLoan/OrigamiAaveV3FlashLoanProvider.sol#L42) 

- AAVE pool that was set above gets deprecated or withdrawn by aave admin and previous address becomes invalid. 

- `OrigamiAaveV3FlashLoanProvider` can never update it's AAVE pool address to the latest one an flashloan calls fail. 
**Attachments**

1. **Proof of Concept (PoC) File**
https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/blob/185a93e25071b6a110ca190e94a6a826e982b2d6/apps/protocol/contracts/common/flashLoan/OrigamiAaveV3FlashLoanProvider.sol#L32

https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/blob/185a93e25071b6a110ca190e94a6a826e982b2d6/apps/protocol/contracts/common/flashLoan/OrigamiAaveV3FlashLoanProvider.sol#L42


```
 IPool public immutable override POOL; 
// ...
    constructor(address _aavePoolAddressProvider) {
        ADDRESSES_PROVIDER = IPoolAddressesProvider(_aavePoolAddressProvider);
        POOL = IPool(ADDRESSES_PROVIDER.getPool());        
    }
```
According to the aave docs [here](https://docs.aave.com/developers/core-contracts/pooladdressesprovider), the pool address should not be hardcoded, and instead the PoolAddressProvider contract should be queried **EVERYTIME** to provide the current pool address. This is because  ** if the pool contract is to be migrated to a new address**, this would break the `OrigamiAaveV3FlashLoanProvider` contract if the address is hardcoded as there is no way to change the aave pool adddress in storage.  

The `PoolAddressProvider` contract never changes and will always provide the latest pool address when queried.

in the ` PoolAddressProvider`, there is a function that allows the AAVE admins to change the `POOL` address returned by [PoolAddressProvider.getPool()](https://github.com/aave/aave-v3-core/blob/6070e82d962d9b12835c88e68210d0e63f08d035/contracts/protocol/configuration/PoolAddressesProvider.sol#L75)  at any time. see [here](https://github.com/aave/aave-v3-core/blob/6070e82d962d9b12835c88e68210d0e63f08d035/contracts/protocol/configuration/PoolAddressesProvider.sol#L57) 

The current implementation in  `OrigamiAaveV3FlashLoanProvider`  goes against the aave integration recommendations, this is classified as a medium severity issue because there may be instances where if pool address is changed, the [flashloan](https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/blob/185a93e25071b6a110ca190e94a6a826e982b2d6/apps/protocol/contracts/common/flashLoan/OrigamiAaveV3FlashLoanProvider.sol#L52C14-L52C23) fcn which calls the pool for a flashloan will no longer work. 

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/58_
