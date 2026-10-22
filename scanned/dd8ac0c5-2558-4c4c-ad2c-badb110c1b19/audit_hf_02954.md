# [M] The getWawa() Function Does Not Return Excess Fees for Wawa NFT(Avatar) Claim

## Summary
Severity: Medium
Contest weight: 0.5773
Dataset id: 16377
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the getWawa() function, the contract WawaNFT.sol requires the users to pay a fee(price) to claim/mint new Wawa NFT(Avatar) tokens.
However, it does not handle the situation where the user pays more msg.value than the required price for this Wawa NFT(Avatar) token. Currently, if msg.value > price, the contract simply accepts the payment without refunding the difference to the user.
The impact is primarily financial, as the current implementation does not return any excess ether msg.value paid beyond the required price = 0.05 ether. Users who pay more than the required price will not get their payment back, resulting in those funds being locked in the WawaNFT.sol contract forever.
The following scenario can happen:
1. Alice wants to claim/mint a new unique Wawa NFT(Avatar).
2. Alice calls the GetWawa.claimWawa() function which internally calls the WawaNFT.getWawa() function and she sends 0.09 ether, but the price of Wawa NFT(Avatar) is 0.05 ether.
3. The price fee is correctly charged at 0.05 ether and Alice successfully gets her Wawa NFT(Avatar), but she is not refunded the excess of 0.04 ether.
4. The excess of 0.04 ether price fee is locked forever in the WawaNFT.sol contract balance.

## Recommendation
To address this vulnerability, we will propose two solutions:
1. Change the check mark for Wawa NFT(Avatar) price to if (msg.value != price), if msg.value is different from price = 0.05 ether the transaction should be reverted:
In this way, you guarantee the user that he will not lose his funds if he accidentally sends a msg.value greater than 0.05 ether because the transaction will revert.
Example:
```solidity
if (msg.value < price) revert InsufficientAmountSent();
if (msg.value != price) revert TheValueDoesNotMatch();
```
2. Return the difference to the user via a call function:
In this way, you will return the difference to the user every time he sends a msg.value greater than the price = 0.05 ether.
Example:
```solidity
uint256 excessPrice = msg.value - price;
(bool success , ) = address(to).call{ value: excessPrice }("");
if (!success) revert FailedPaymentToUser();
```
