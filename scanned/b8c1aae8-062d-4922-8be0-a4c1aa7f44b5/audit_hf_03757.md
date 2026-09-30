# [M] secondary markets are problematic with how locking works

## Summary
Severity: Medium
Contest weight: 0.2499
Dataset id: 19920
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Seeing that a pool is about to lock, an attacker can use a flash loan from a secondary market like Uniswap to claim the share of a potential unlock of capital later.
The timestamp a pool switches to Late can be predicted and an attacker can use this to call assessState which is callable by anyone. This will trigger the pool to move from Active/LateWithinGracePeriod to Late calling lockCapital on the ProtectionPool:
ProtectionPool.sol#L365-L366
File: ProtectionPool.sol
365:
/// step 1: Capture protection pool's current investors by creating a snapshot of the token balance by using ERC20Snapshot in SToken
366:
_snapshotId = _snapshot();
This records who is holding sTokens at this point in time. If the borrower makes a payment and the pool turns back to Active, later the locked funds will be available to claim for the sToken holders at that snapshot:
DefaultStateManager.sol#L500-L505
File: DefaultStateManager.sol
500:
/// The claimable amount for the given seller is proportional to the seller's share of the total supply at the snapshot
501:
/// claimable amount = (seller's snapshot balance / total supply at snapshot) * locked capital amount
502:
_claimableUnlockedCapital =
503:
(_poolSToken.balanceOfAt(_seller, _snapshotId) *
504:
lockedCapital.amount) /
505:
_poolSToken.totalSupplyAt(_snapshotId);
From docs:
If sellers wish to redeem their capital and interest before the lockup period, they might be able to find a buyer of their sToken in a secondary market like Uniswap. Traders in the exchanges can long/short sTokens based on their opinion about the risk exposure associated with sTokens.
Since an sToken is a fungible ERC20 token, it is fairly easy to bootstrap the secondary markets for protection sellers.
If there is a Uniswap (or similar) pool for this sToken, an attacker could potentially, using a flash loan, trigger the switch to Late and since they will be the ones holding the sTokens at the point of locking they will be the ones that can claim the funds at a potential unlock.
An attacker can, using a flash loan from a secondary market like Uniswap, steal a LPs possible share of unlocked tokens. Only paying the risk of the flash loan fee.

## Recommendation
I recommend you make assessState only callable by a trusted user. This would remove the attack vector, since you must hold the tokens over a transaction. It removes the possibility to "flash-lock".
