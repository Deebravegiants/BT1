# [M] Keeper can make deposits/orders/withdrawals fail by providing limited gas

## Summary
Severity: Medium
Contest weight: 0.4576
Dataset id: 19864
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Malicious keeper can make execution of deposits/orders/withdrawals fail by providing limited gas to the execution. If enough gas is sent for the cancellation to succeed but for the execution to fail the keeper is able to receive the execution fee + incentive rewards and cancel all deposits/orders/withdrawals. Keepers can execute any deposits/orders/withdrawals. All executions are attempted and if they fail, they are cancelled and the keeper is paid for the execution fee + rewards. Example for executing deposits:
cts/exchange/DepositHandler.sol#L92
```solidity
function executeDeposit(
bytes32 key,
OracleUtils.SetPricesParams calldata oracleParams
) external
globalNonReentrant
onlyOrderKeeper
withOraclePrices(oracle, dataStore, eventEmitter, oracleParams)
{
uint256 startingGas = gasleft();
try this._executeDeposit(
key,
oracleParams,
msg.sender,
startingGas
) {
} catch (bytes memory reasonBytes) {
_handleDepositError(
key,
startingGas,
reasonBytes
);
}
}
```
For the attack to succeed, the keeper needs to make this._executeDeposit revert. Due to the 64/63 rule the attack will succeed if both of the following conditions meet:
1. 63/64 of the supplied gas will cause an out of gas in the try statement
2. 1/64 of the supplied gas is enough to execute the catch statement.
Considering 2000000 is the max callback limit and native token transfer gas limit is large enough to support contracts the above conditions can be met.
I created a POC that exploits the vulnerability on deposits. Keep in mind that it might be easier (lower limits) for Orders as more logic is performed in the try statement and therefore more gas is supplied. See in the Code Snippet section
1. Keeper can remove all deposits/withdrawals/orders from the protocol.
1. Essentially stealing all execution fees paid
1. Keeper can create deposits and by leveraging the bug can cancel them when executing while receiving rewards.
1. Vaults will be drained

## Recommendation
Add a buffer of gas that needs to be supplied to the execute function to make sure the try statement will not revert because of out of gas.
