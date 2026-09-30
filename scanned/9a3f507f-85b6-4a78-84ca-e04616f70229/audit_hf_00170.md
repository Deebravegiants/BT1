# [M] use of transfer

## Summary
Severity: Medium
Contest weight: 0.2061
Dataset id: 920
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Use of `transfer()` might render ETH impossible to withdraw because after istanbul hardfork, there is an increase in the gas cost of the SLOAD operation and therefore breaks some existing smart contracts. Those contracts will break because their fallback functions used to consume less than 2300 gas, and they’ll now consume more, since 2300 the amount of gas a contract’s fallback function receives if it’s called via Solidity’s `transfer()` or `send()` methods. Any smart contract that uses `transfer()` or `send()` is taking a hard dependency on gas costs by forwarding a fixed amount of gas: 2300.

* <https://consensys.net/diligence/blog/2019/09/stop-using-soliditys-transfer-now/>
* <https://blog.openzeppelin.com/opyn-gamma-protocol-audit/>

## Proof of Concept
* <https://github.com/sushiswap/miso/blob/2cdb1486a55ded55c81898b7be8811cb68cfda9e/contracts/MISOTokenFactory.sol#L242>
* <https://github.com/sushiswap/miso/blob/2cdb1486a55ded55c81898b7be8811cb68cfda9e/contracts/MISOMarket.sol#L256>
* <https://github.com/sushiswap/miso/blob/2cdb1486a55ded55c81898b7be8811cb68cfda9e/contracts/MISOLauncher.sol#L251>
* <https://github.com/sushiswap/miso/blob/2cdb1486a55ded55c81898b7be8811cb68cfda9e/contracts/MISOFarmFactory.sol#L244>

## Recommendation
use `call()` to send eth

This is intentional, not a risk. The contract does not want to give any gas stipend to the destination.

Even if the user messes up, `misoDev` address can be changed to a proper address later.

using `.transfer` can make ETH transfer to a smart contract impossible. User can always change the address however I agree with warden that this is an issue.
