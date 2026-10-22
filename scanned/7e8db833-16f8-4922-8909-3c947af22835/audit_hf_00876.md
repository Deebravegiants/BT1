# [M] MasterAMO should not use the

## Summary
Severity: Medium
Contest weight: 0.6053
Dataset id: 2632
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
MasterAMO is a utils contract that intended to be inherited by V2AMO, V3AMO contracts, therefore. it's initializer function should not use the initializer modifier, instead, it should use onlyInitializing modifier. In the MasterAMO.sol:104 contract, the initialize function uses the initializer modifier. This is incorrect for a contract like MasterAMO, which is meant to be inherited by other contracts, such as V2AMO and V3AMO. In this inheritance model, the V2AMO contract also has its own initialize function, which includes the initializer modifier and calls the initialize function of MasterAMO. The problem here is that both the parent contract MasterAMO and the child contracts V2AMO, V3AMO are using the initializer modifier, which limits initialization to only one call. According to the OpenZeppelin documentation, the onlyInitializing modifier should be used to allow initialization in both the parent and child contracts. The onlyInitializing modifier ensures that when the initialize function is called, any contracts in its inheritance chain can still complete their own initialization. https://docs.openzeppelin.com/contracts/4.x/api/proxy#Initializable-initializer-- A modifier that defines a protected initializer function that can be invoked at most once. In its scope, onlyInitializing functions can be used to initialize parent contracts. Internal pre-conditions External pre-conditions Attack Path In this scenario, no direct attack or monetary loss is likely. However, the vulnerability causes a significant operational issue, preventing inheriting contracts from completing initialization. This could lead to a failure in the deployment of critical protocol components, affecting the overall system functionality.

## Recommendation
Replace the initializer modifier in the MasterAMO contract with the onlyInitializing modifier. This allows the initialize function to be used by both the MasterAMO and any inheriting contracts during their initialization phase, without conflicting with their individual setup processes.
```solidity
function initialize(
    address admin, // Address assigned the admin role (given exclusively to a multi-sig wallet)
    address boost_, // The Boost stablecoin address
    address usd_, // generic name for $1 collateral ( typically USDC or USDT )
    address pool_, // The pool where AMO logic applies for Boost-USD pair
    // On each chain where Boost is deployed, there will be a stable Boost-USD pool ensuring BOOST's peg.
    // Multiple Boost-USD pools can exist across different DEXes on the same chain, each with its own AMO, maintaining independent peg guarantees.
    address boostMinter_ // the minter contract
) public initializer {
```
```solidity
function initialize(
    address admin, // Address assigned the admin role (given exclusively to a multi-sig wallet)
    address boost_, // The Boost stablecoin address
    address usd_, // generic name for $1 collateral ( typically USDC or USDT )
    address pool_, // The pool where AMO logic applies for Boost-USD pair
    // On each chain where Boost is deployed, there will be a stable Boost-USD pool ensuring BOOST's peg.
    // Multiple Boost-USD pools can exist across different DEXes on the same chain, each with its own AMO, maintaining independent peg guarantees.
    address boostMinter_ // the minter contract
) public onlyInitializing {
```
