# [M] Incompatibility with revert-on-zero-transfer

## Summary
Severity: Medium
Contest weight: 0.7250
Dataset id: 22793
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Per the contest README, revert-on-zero-transfer tokens should be considered for We show that the contract is incompatible with revert-on-zero-transfer tokens in certain valid inputs, causing reverts. We use Maradona as the example. The same idea applies to Messi. In tryToChargeFees(), the fee values are calculated based on feeRateBps with several case handling:
```solidity
uint256 feeValueForFeeReceiver = (amount * feeRateBps) / 10000; // (A)
uint256 feeValueForTerrace = (feeValueForFeeReceiver * txFeeBps) / 10000;
uint256 minFeeValueForTerrace = (amount * minTerraceFeeBps) / 10000;
uint256 adjustedFeeValueForTerrace = feeValueForTerrace > minFeeValueForTerrace ? feeValueForTerrace : minFeeValueForTerrace;
uint256 adjustedFeeValueForFeeReceiver = feeValueForTerrace > minFeeValueForTerrace ? feeValueForFeeReceiver - feeValueForTerrace : feeValueForFeeReceiver; // (B)
```
The feeRateBps is supplied by the sponsor/user/whoever triggers the swap on behalf:
```solidity
function takeTokensAndTrade(
    OperationParameters[] memory ops,
    address feeReceiver,
    address receivingUser,
    address feesTokenAddress
) public payable override noReentrancy notPaused{
```
If the feeRateBps is supplied to be zero, then line (A) will calculate feeValueForFeeReceiver to be zero, which leads to (B) calculating adjustedFeeValueForFeeReceiver to also be zero. Then a zero-value transfer will be triggered at line 263:
```solidity
IERC20 feeToken = IERC20(feeTokenAddress);
uint256 balance = feeToken.balanceOf(address(this));
if (balance >= adjustedFeeValueForFeeReceiver + adjustedFeeValueForTerrace) {
    feeToken.safeTransfer(feeReceiver, adjustedFeeValueForFeeReceiver); //
```
Thereby causing the tx to revert. There are valid use cases where the caller will want to use a zero fee rate, for example: • The Messi Sponsor may want to enable free swapping as a promotional event, or waivering fees for a special group of customers. • Protocols building on top of Maradona may want to enable the same kind of discount for their users. Incompatibility with revert-on-zero-transfer, breaking invariant of the protocol

## Proof of Concept
```solidity
Add the following function into MockERC20 contract
function transfer(address to, uint256 value) public virtual override returns (bool) {
    if (value == 0) revert("ERC20: Zero value on transfer");
    return super.transfer(to, value);
}
```
Then run make tests/Maradona and make tests/Messi, the tests will fail with the following logs: Maradona 1 failing 1) Maradona Trade execution From ETH to token Should allow to make a single hop trade and charge 5 bps in token: Error: VM Exception while processing transaction: reverted with reason string 'ERC20: Zero value on transfer' Messi 11 failing 1) Messi Trade execution From token to ETH Should allow to make a single hop trade: Error: VM Exception while processing transaction: reverted with reason string 'ERC20: Zero value on transfer' All of the failed tests have the exact reason string as ERC20: Zero value on transfer reasoning, proving that zero transfer is indeed the problem.

## Recommendation
Check the transfer amount before each transfer call (don't perform the transfer if the amount is zero)
