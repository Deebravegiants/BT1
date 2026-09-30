# [M] `PartyGovernanceNFT#rageQuit`

## Summary
Severity: Medium
Contest weight: 0.6429
Dataset id: 19445
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the PartyGovernanceNFT.rageQuit function where the contract calculates a withdrawal amount for each ERC20 token and then guards the minimum‑withdrawal validation with an if (amount > 0) condition. Because the check that enforces the user‑provided minWithdrawAmounts array is placed inside this conditional, any token for which the Party holds a zero balance produces an amount equal to 0 and bypasses the validation entirely. As a result the function proceeds to burn the caller’s governance NFT and reduce the caller’s voting power while transferring no assets, effectively causing the user to lose their NFT and any expected refund. This situation occurs when a participant attempts to rage quit after the Party’s balance for a particular ERC20 has been drained, for example by a prior proposal that transferred all USDC out of the Party. The affected parties are any holders of PartyGovernanceNFT who rely on the minWithdrawAmounts guarantee to receive at least a minimal amount of tokens on exit. The issue was discovered during a Code4rena audit through a targeted test that set the ERC20 balance to zero, supplied a non‑zero minWithdrawAmount, and observed that the NFT was burned with no token transfer. The bug is subtle because the function appears to perform a minimum‑withdrawal check, yet the guard condition silently skips the check for zero amounts, making the loss visible only after the NFT has been destroyed. The impact is a loss of governance rights and funds that the user expected to receive, violating the contract’s accounting assumptions that a user either receives the requested minimum or the transaction reverts. To remediate the flaw the conditional should be changed to if (amount >= 0) or the minimum‑withdrawal verification should be moved outside the amount‑greater‑than‑zero guard so that a zero amount still triggers a revert when it is below the user’s minimum. This adjustment restores the intended safety check and prevents accidental NFT burning without compensation.

## Proof of Concept
Consider the following scenario illustrating the issue:

1. A Party holds `USDC` tokens.
2. The entire `USDC` balance is transferred to another account, e.g., via a proposal.
3. Alice, unaware of the Party’s depleted `USDC` holdings, attempts to `rageQuit()`.
4. Alice specifies minimum withdrawal amounts using `uint256[] minWithdrawAmounts`.
5. Despite specifying `minWithdrawAmounts`, all of Alice’s Party tokens are burned, and she receives nothing in return.

In `PartyGovernanceNFT#rageQuit()` the withdrawl amount for each ERC20 is calculated as follows:
```solidity
withdrawAmounts[i] += (balance * getVotingPowerShareOf(tokenIds[j])) / 1e18;
```
Where:
```solidity
balance = uint256 balance = address(withdrawTokens[i]) == ETH_ADDRESS ? address(this).balance : withdrawTokens[i].balanceOf(address(this));
```
However, if the token is an ERC20 for which the Party does not have any remaining balance, `withdrawAmounts[i]` would be equal to `0`.

This means the following check would not be executed at all:
```solidity
if (amount > 0) {
    // ...
    // Check amount is at least minimum.
    if (amount < minAmount) {
        revert BelowMinWithdrawAmountError(amount, minAmount);
    }

    // ...
    payable(receiver).transferEth(amount);
}
```
Since the check for the minimum withdrawal amount is within the `if` statement, it is never executed when `amount` is equal to `0`, leading to unintended NFT loss.

```solidity
uint96 totalVotingPowerBurned = _burnAndUpdateVotingPower(tokenIds, !isAuthority_); 

// Update total voting power of party.
_getSharedProposalStorage().governanceValues.totalVotingPower -= totalVotingPowerBurned;

// Add this to PartyGovernanceNFT.t.sol
function testRageQuitDoesNotHonorMinWithdrawAmountIsERC20BalanceIsZero() external {
    // Create party
    (Party party, , ) = partyAdmin.createParty(
        partyImpl,
        PartyAdmin.PartyCreationMinimalOptions({
            host1: address(this),
            host2: address(0),
            passThresholdBps: 5100,
            totalVotingPower: 100,
            preciousTokenAddress: address(toadz),
            preciousTokenId: 1,
            rageQuitTimestamp: 0,
            feeBps: 0,
            feeRecipient: payable(0)
        })
    );

	// Configure rage quit
    vm.prank(address(this));
    party.setRageQuit(uint40(block.timestamp) + 1);

	// Give alice 10 voting tokens out of 100
    address alice = makeAddr("alice");
    vm.prank(address(partyAdmin));
    uint256 tokenId = party.mint(alice, 10, alice);

	// An ERC20 in which the party previously had holdings
	// but now it's balance is == 0.
    IERC20[] memory tokens = new IERC20[](1);
    tokens[0] = IERC20(address(new DummyERC20()));

	// The minimum withdraw alice is willing to accept
    uint256[] memory minWithdrawAmounts = new uint256[](1);
    minWithdrawAmounts[0] = 1;

    uint256[] memory tokenIds = new uint256[](1);
    tokenIds[0] = tokenId;

    // Make sure the party has 0 balance
    DummyERC20(address(tokens[0])).deal(address(party), 0);

    // Before
    assertEq(party.votingPowerByTokenId(tokenId), 10);
    assertEq(tokens[0].balanceOf(alice), 0);

    vm.prank(alice);
    party.rageQuit(tokenIds, tokens, minWithdrawAmounts, alice);

    // After
    assertEq(party.votingPowerByTokenId(tokenId), 0);
    assertEq(tokens[0].balanceOf(alice), 0);
    assertEq(party.getGovernanceValues().totalVotingPower, 90);
}
```

## Recommendation
To ensure that the `BelowMinWithdrawAmountError` check is performed even when `amount` is equal to `0`, `amount > 0` must be replaced with `amount >= 0` in the `rageQuit()` function. Here’s the modified code snippet:
```diff
--- a/contracts/party/PartyGovernanceNFT.sol
+++ b/contracts/party/PartyGovernanceNFT.sol
@@ -418,17 +418,17 @@ contract PartyGovernanceNFT is PartyGovernance, ERC721, IERC2981 {
                      // Transfer fee to fee recipient.
                      if (address(token) == ETH_ADDRESS) {
                          payable(feeRecipient).transferEth(fee);
                      } else {
                          token.compatTransfer(feeRecipient, fee);
                      }
                  }

-                if (amount > 0) {
+                if (amount >= 0) {
                      uint256 minAmount = minWithdrawAmounts[i];

                      // Check amount is at least minimum.
                      if (amount < minAmount) {
                          revert BelowMinWithdrawAmountError(amount, minAmount);
                      }

                      // Transfer token from party to recipient.
```
