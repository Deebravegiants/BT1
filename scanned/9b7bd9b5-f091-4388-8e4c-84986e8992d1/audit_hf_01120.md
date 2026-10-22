# [H] UniswapV2Locker.claimFeesAndExit() Cannot Be Called, Resulting in Locked Funds

## Summary
Severity: High
Reporter: KupiaSec, also found by trachev, etherhood, valkvalue and 0xacnologiac
Contest weight: 0.7460
Dataset id: 4591
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The UniswapV2Locker.claimFeesAndExit() function can only be executed by its owner. The UniswapV2Migrator contract creates the UniswapV2Locker contract, and the constructor of UniswapV2Locker assigns ownership to the UniswapV2Migrator. However, the UniswapV2Migrator, despite being the owner of UniswapV2Locker, does not contain any logic to call the claimFeesAndExit() function. As a result, the Uniswap V2 pool shares held by the UniswapV2Locker, which were transferred during the migration, cannot be claimed, leading to locked funds.
• UniswapV2Migrator.sol:
```solidity
constructor(address airlock_, IUniswapV2Factory factory_, IUniswapV2Router02 router) {
    // ...
    locker = new UniswapV2Locker(Airlock(payable(airlock)), factory, this);
}
```
• UniswapV2Locker.sol:
```solidity
constructor(Airlock airlock_, IUniswapV2Factory factory_, UniswapV2Migrator migrator_)
    Ownable(msg.sender) {
    // ...
}
```

Impact Explanation:
High. Funds cannot be claimed and remain frozen.

## Recommendation
Transfer ownership to the timelock contract after migration.
