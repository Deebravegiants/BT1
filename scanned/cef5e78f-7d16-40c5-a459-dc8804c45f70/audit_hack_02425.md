# [M] Lack of `__gap` Variable

## Summary
Severity: Medium
Source: https://github.com/matter-labs/zksync-2-contracts/blob/9f3c6944e6320166edd96ef6586a9dd4548a27f2/ethereum/contracts/bridge/L1ERC20Bridge.sol
Type: audit-issue

## Details
The [L1ERC20Bridge](https://github.com/matter-labs/zksync-2-contracts/blob/9f3c6944e6320166edd96ef6586a9dd4548a27f2/ethereum/contracts/bridge/L1ERC20Bridge.sol) and [L2StandardERC20](https://github.com/matter-labs/zksync-2-contracts/blob/9f3c6944e6320166edd96ef6586a9dd4548a27f2/zksync/contracts/bridge/L2StandardERC20.sol) contract are intended to be used as logic contracts with a proxy, but do not have a `__gap` variable. This would become problematic if a subsequent version was to inherit one of these contracts. If the derived version were to have storage variables itself and additional storage variables were subsequently added to the inherited contract, a storage collision would occur.

Consider appending a [\_\_gap variable](https://docs.openzeppelin.com/contracts/4.x/upgradeable#storage%5Fgaps) as the last storage variable to these upgradeable contracts, such that the storage slots sum up to a fixed amount (e.g. 50). This will proof any future storage layout changes to the base contract. Note that the `__gap` variable space will need to be adjusted accordingly as subsequent versions include more storage variables, in order to maintain the fixed amount of slots (e.g. 50).

_**Update:** Acknowledged, not resolved. The Matter Labs team stated:_

> _While we appreciate your insights and suggestions, we do not believe the issue has a significant security risk. Specified contracts are not expected to be inherited, since they are complete logical contracts._
