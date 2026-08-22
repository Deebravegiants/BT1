# [H] Beebots.randomIndex() Can Be Manipulated To Not Be Random Without Costing Alice Anything

## Summary
Severity: High
Chain: Smart contract
Component: 2021-04-meebits
Published: 2021-05-01
Source: https://github.com/code-423n4/2021-04-meebits-findings/issues/85
Type: code-finding

## Details
# Handle

jvaqa


# Vulnerability details

## Impact

Beebots.randomIndex() Can Be Manipulated To Not Be Random Without Costing Alice Anything.

Since lower-numbered ids are seemingly more valuable, a malicious attacker can manipulate randomIndex() to give themselves a more desirable value at no cost to themselves.

Alice can create a contract that calls Beebots.mint(), and then reverts if the randomValue that Beebots produced was not desirable, and use Flashbots to only pay for the transaction if she receives the random value that she wants.
If Alice were naive, she could call her contract repeatedly on-chain, never paying Beebots the minting fee until she gets the random value that she desires, but still paying gas fees for failed transactions.
However, Alice doesn't even need to pay gas fees for failed transactions. To avoid paying gas fees for each of the failed mints, Alice can use the Flashbots function FlashbotsCheckAndSend, which only publishes the mint() transaction if Alice receives the value that she desires from Beebots.mint().
Thus, since Beebots does not use a commit-reveal scheme or some other two step process for random number generation, the random numbers from Beebots are completely gameable.

## Proof of Concept

functionn AliceAttackerFunction() public {
  uint256 desiredBeebotsId = 1;
  uint256 mintedId = Beebots.mint{value:costOfMinting}();
  require(mintedId == desiredBeebotsId);
  block.coinbase.transfer(flashbotsReward);
}

## Recommended Mitigation Steps
If it is important to retain randomness in producing ids (perhaps lower numbered ids are more valuable), then you need to use a two-step commit-reveal scheme for minting. You can have users only do the commit step if you like, and then batch call the redeems for your users.
If you want to mint in a single transaction, then the random nftIds are gameable, and users can use flashBots to get whatever nftId they would like.
