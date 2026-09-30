# [M] Malicious or compromised admin of certain

## Summary
Severity: Medium
Contest weight: 0.4415
Dataset id: 20294
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
are marked as "Restricted" (Not Trusted). This means that any potential issues arising from the external protocol's admin actions (maliciously or Q: Are the admins of the protocols your contracts integrate with (if any) TRUSTED or RESTRICTED? RESTRICTED (LSTs) where the admin could upgrade the token contract code. Those examples are omitted for brevity, as the write-up and mitigation are the same and would duplicate this issue. (swETH). Liquid Staking Tokens • swETH: 0xf951E335afb289353dc249e82926178EaC7DEd78 Upon inspection of the swETH on-chain contract, it was found that it is a Transparent Upgradeable Proxy. This means that the admin of Swell protocol could upgrade the contracts. Tokemak relies on the swEth.swETHToETHRate() function to determine the price of the swETH LST within the protocol. Thus, a malicious or compromised admin of Swell could upgrade the contract to have the swETHToETHRate function return an extremely high to manipulate the total values of the vaults, resulting in users being able to withdraw more assets than expected, thus draining the LMPVault. File: SwEthEthOracle.sol 26:
```solidity
function getPriceInEth(address token) external view returns (uint256 price) {
27:
    // Prevents incorrect config at root level.
28:
    if (token != address(swEth)) revert Errors.InvalidToken(token);
29:
30:
    // Returns in 1e18 precision.
31:
    price = swEth.swETHToETHRate();
32:
}
```
Loss of assets in the scenario as described above.

## Recommendation
implementing additional controls to reduce the risks. Review each of the supported LSTs and determine how much power the Liquid the token contracts or have the ability to update the exchange rate/price to an arbitrary value without any limit), those LSTs should be subjected to additional controls or monitoring, such as implementing some form of circuit breakers if the price deviates beyond a reasonable percentage to reduce the negative impact to Tokemak if it happens.
