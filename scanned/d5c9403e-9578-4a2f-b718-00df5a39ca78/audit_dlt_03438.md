# [H] A Vault can steal all funds from another Vault through the Registry's flash loan contract due to insufficient access control in `Connector.sendTokensToTrustedAddress()`

## Summary
Severity: High
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1327
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/BalancerFlashLoan.sol#L79-L82
https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/helpers/BaseConnector.sol#L98-L100


# Vulnerability details

## Impact
The keeper of a Vault can steal all funds from another Vault. 
## Proof of Concept
Noya Vaults are registered with the `Registry` contract where `Registry.addVault()` is used to add a particular Vault and specify the address of its `AccountingManager`, `maintainer`, `keeper`, etc. The `Registry` contract also has the state variable address `flashLoan` which is the address of a `BalancerFlashLoan` contract that is used by the Vaults to leverage flash loans. The issue is that in any Connector, the `BaseConnector.sendTokensToTrustedAddress()` function allows the `BalancerFlashLoan` contract to perform token transfers back to the `BalancerFlashLoan` contract - [code snippet](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/helpers/BaseConnector.sol#L98-L99). This allows for the following exploit:
* Assume 2 Vaults with Ids: ID-1 and ID-2
* Assume ID-1 has a Connector C-1
* Assume ID-2 has a Connector C-2
* Assume C-2 holds X amount of token Y
* The keeper of ID-1 calls `BalancerFlashLoan.makeFlashloan()` [code snippet](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/BalancerFlashLoan.sol#L37-L44)
* the `tokens` array holds the address of some token
* the `amounts` array holds some amount of the token in `tokens`
* `bytes userData` is packed as
	 * `uint256 vaultId = ID-1`
	 * `address receiver = C-1`
	 * `address[] destinantionConnector = [C-2, Y]`
	 * `bytes[] callingData = 
	 [sendTokensToTrustedAddress(Y, X, address(0), ""),
	 transferTo(C1, X)]`
	 * `uint256[] gas = [enoughGas, enoughGas]`
* `BalancerFlashLoan.receiveFlashLoan()` is called by Balancer
* The `receiver` (`C-1`) get's the flash loan tokens
* `destinationConnector[0].call{...}(callingData[0])`, which is the `BaseConnector.sendTokensToTrustedAddress()` call to `C-2`. The Connector `C-2` allows the execution since `msg.sender` is `registry.flashLoan()`. `C-2` sends X amount of tokens to `BalancerFlashLoan`. 
* `destinationConnector[1].call{...}(callingData[1])`, which is the `Y.transferTo()` call that will transfer the X amount of tokens from `BalancerFlashLoan` to `C-1`. 
* `C-1` returns the borrowed tokens and keeps the X amount of token Y

## Coded POC
The aim of the POC is to showcase how one Vault can steal the funds from another Vault's `BaseConnector`. The test consists of 2 Vaults (ID-5 and ID-10).  In the beginning of the test
ID-5 receives and executes deposits that go into its `BaseConnector`. The keeper of ID-10 then leverages the `BalancerFlashLoan` contract to call `BaseConnector.sendTokensToTrustedAddress()` and after that to retrieve the funds into an arbitrary address. 

* Add the contents of the following gist in a solidity file under `/testsFoundry` - [gist with code](https://gist.github.com/alexxander77/fd48ea07b66e8e6896896467ba594cad)

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1327_
