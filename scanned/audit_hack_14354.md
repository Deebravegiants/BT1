# [H] Timestamp Dependency Vulnerability Allows Manipulation of Auction Price

## Summary
Severity: High
Reporter: BugBusters
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L99
Type: audit-issue

## Details
# Timestamp Dependency Vulnerability Allows Manipulation of Auction Price

## Summary
Timestamp Dependency Vulnerability in the `getPrice()` function allows an attacker to manipulate the current price of the auction by front-running transactions and manipulating the timestamp.

## Vulnerability Detail
The vulnerability lies in the `getPrice()` function, which calculates the current price of the auction based on the current timestamp (block.timestamp). This dependency on the timestamp allows an attacker to submit a transaction with a manipulated timestamp, causing the function to return a different price than intended.

## Impact
By exploiting this vulnerability, an attacker can manipulate the auction's current price, potentially gaining an unfair advantage in the auction. They can front-run transactions to execute trades at more favorable prices, potentially undermining the integrity and fairness of the auction process.

## Code Snippet
```solidity
function getPrice() public view returns (uint256) {
    // Use the current timestamp to get the current price
    return getPriceAt(block.timestamp);
}
```
https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L99
## Tool used

Manual Review

## Recommendation
To address this vulnerability, consider using a more secure source of timestamp, such as a block number or an external oracle, to calculate the current price. Relying on a more secure and tamper-resistant timestamp source can prevent front-running attacks and ensure the integrity of the auction's price calculation.
