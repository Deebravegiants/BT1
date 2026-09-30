# [H] Possible DoS On Forced Destruction Of LendingPool

## Summary
Severity: High
Contest weight: 0.6326
Dataset id: 11690
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Augmented Finance protocol's main LendingPool contract takes a proxy-based implementation where the proxy contract is deployed at the front-end while the logic contract contains the actual business logic implementation. Specifically, it takes a delegatecall-based proxy pattern so that each component is split into two contracts: a back-end logic contract (that holds the implementation) and a front-end proxy (that contains the data and uses delegatecall to interact with the logic contract). From the user's perspective, they interact with the proxy while the code is executed on the logic contract. Moreover, to accommodate increased contract code size, the protocol splits the liquidation functionalities into another contracts LendingPoolCollateralManager. Note that both contracts can be queried from the MarketAccessController registry.
```solidity
function initialize(IMarketAccessController provider) public initializer(POOL_REVISION) {
    _addressesProvider = provider;
    _maxStableRateBorrowSizePct = 25 * PercentageMath.PCT;
    _flashLoanPremiumPct = 9 * PercentageMath.BP;
    _maxNumberOfReserves = 128;
}
```
Our analysis shows that the current implementation may suffer from a denial-of-service (DoS) by forcing the LendingPool to self-destruct. Specifically, a malicious user Malice may call initialize() on the back-end logic contract of LendingPool, not the proxy. With that, the initialize() call successfully bypasses the validation from the modifier initializer(POOL_REVISION) and populates a malicious provider, which can be queries to return a controlled collateralManager. After that, Malice calls liquidationCall() to execute the code from collateralManager in the context of the logic contract of LendingPool. Since the collateralManager contract is controlled, it may simply execute self-destruct to destroy the LendingPool logic, which immediately corrupts the execution of the entire protocol.

## Recommendation
Ensure the LendingPool::initialize() call cannot be bypassed to thwart the above denial-of-service attack.
