# [H] Re-entrancy Vulnerable Vector on `mint()` function

## Summary
Severity: High
Reporter: moneyversed
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L161-L169
Type: audit-issue

## Details
# Re-entrancy Vulnerable Vector on `mint()` function

## Summary

MeritDutchAuction contract is susceptible to a re-entrancy attack. The vulnerability lies in the function `mint()`.

## Vulnerability Detail

Re-entrancy vulnerabilities occur when a contract is forced into a state where it calls out to another contract before it has resolved its state. If the called contract calls back into the original before the state is resolved, it could have unexpected results. The `mint()` function sends a refund if the user sent more ether than required for the transaction, but it does this before emitting the `Minted` event and updating the state.

## Impact

If a contract that has a fallback function that calls the `mint()` function is used, it can potentially mint multiple NFTs without updating the minted count and mintedPerAddress count, as well as taking advantage of the refund to drain the contract of its balance.

## Code Snippet

```solidity
if(msg.value > totalPaid) {
    // If too much ETH was sent, refund the difference
    (bool success, ) = payable(msg.sender).call{value: msg.value - totalPaid}(bytes(""));
    require(success, "Refund failed");
}

// Emit event for offchain integrations
emit Minted(msg.sender, amount, pricePaid);
```

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L161-L169

## Tool used

Manual Review

## Recommendation

It's best to follow the Checks-Effects-Interactions pattern to avoid re-entrancy attacks. Make sure all internal state changes occur before calling external contracts. You should make sure to emit the `Minted` event and update the `minted` and `mintedPerAddress` state variables before the refund is processed.

## Proof Of Concept

Create a contract that calls the `mint()` function in its fallback function. Send a transaction to the `mint()` function with more ether than needed for the transaction. The contract will then be in a state where it can call back into the `mint()` function before the state has been updated, potentially creating more NFTs than the limit or draining the contract of its balance.
