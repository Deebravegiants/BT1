# [H] Keepers will suffer significant losses due to undercompensation of L1 fees

## Summary
Severity: High
Contest weight: 0.7790
Dataset id: 20261
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As shown in keep() modifier (L40-57), only L2 execution fee are compensated. File: perennial-v2\packages\perennial-oracle\contracts\pyth\PythOracle.sol 124:
```solidity
function commitRequested(uint256 versionIndex, bytes calldata updateData)
    public
    payable
    keep(KEEPER_REWARD_PREMIUM, KEEPER_BUFFER, "")
{
...
157:
}
```
File: perennial-v2\packages\perennial-extensions\contracts\MultiInvoker.sol 359:
```solidity
function _executeOrder(
    address account,
    IMarket market,
    uint256 nonce
) internal keep (
    GAS_BUFFER,
    abi.encode(account, market, orders(account, market, nonce).fee)
) {
...
384:
}
```
File: root\contracts\attribute\Kept.sol 40:
```solidity
uint256 startGas = gasleft();
_;
uint256 gasUsed = startGas - gasleft();
uint256 keeperFee = _scaleGas(gasUsed, multiplier, buffer)
    .mul(multiplier)
    .mul(_etherPrice())
    .div(1e18);
_raiseKeeperFee(keeperFee, data);
keeperToken().push(msg.sender, keeperFee);
emit KeeperCall(msg.sender, gasUsed, multiplier, buffer, keeperFee);
57:
}
```
Takes a random selected transaction at the writing time https://optimistic.etherscan.io/tx/0xbb8e68e21c92acf4171fb6041b758b55acc3c559ec4595ed1129d534d90de995 We can find the L1 fee is much expensive than L2 fee. L2 fee = 0.06 Gwei * 113,449 ~= 6,806 Gwei L1 fee = 0.00006565634612417 ETH ~= 65656 Gwei L1 / L2 = 964% Typically, L1 fees are dynamic and determined by the calldata length and smoothed Ethereum gas prices. To submit Pyth oracle price, the VAA calldata will be 1700+ bytes, keepers need to pay much L1 rollup fee. https://github.com/equilibria-xyz/perennial-v2/packages/perennial-oracle/test/integration/pyth/PythOracle.test.ts#L34 No enough incentive for keeper to submit oracle price and execute orders, the system will not work.

## Recommendation
Compensating L1 rollup fee, here are some reference: https://docs.arbitrum.io/arbos/l1-pricing https://community.optimism.io/docs/developers/build/transaction-fees/#the-l1-data-fee
