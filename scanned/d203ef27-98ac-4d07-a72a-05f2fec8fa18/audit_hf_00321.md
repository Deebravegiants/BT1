# [M] Deactivate function can be bypassed

## Summary
Severity: Medium
Contest weight: 0.4308
Dataset id: 1579
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a logic flaw in the token‑sheltering contract that allows a privileged client to bypass the intended grace‑period deadline for deactivating a token and withdraw the entire token balance to its own address. The contract records the timestamp of the last activation of a token in a mapping called activated and only permits deactivation while activated[_token] + GRACE_PERIOD is greater than the current block timestamp. However, the activate function can be called repeatedly by the same client; each call overwrites the stored timestamp with the current block time. As a result, after the original grace period has elapsed, the client can simply invoke activate again, which resets the activation timestamp, thereby extending the window during which deactivate will succeed. The client then calls deactivate and triggers the transfer of all tokens that were held for other users back to itself, effectively rugging the protocol. The impact is that any user who deposited tokens into the shelter expects their assets to be secured for the duration of the grace period, but instead sees their balance disappear, receiving no refunds or withdrawals. This condition occurs only when the caller possesses the onlyClient role, which is assumed to be trustworthy, and when the contract does not enforce a one‑time activation check. The issue was discovered during a manual audit by the Code4rena team, which derived a proof‑of‑concept that steps through activation, waiting for the grace period to expire, re‑activating to reset the timestamp, and finally deactivating to extract the funds. The flaw can be hard to notice because the deactivate function correctly validates the deadline against the stored timestamp, giving the appearance of a sound time‑based restriction, while the ability to overwrite that timestamp is hidden in the activate function’s lack of guard against repeated calls. Conceptually, the fix is to make activation a one‑time operation per token, for example by requiring that activated[_token] be zero before allowing a new activation, or by storing an immutable activation flag that prevents the timestamp from being reset after the first activation. By doing so, the contract would preserve the intended accounting invariant that funds remain locked until the grace period ends, preventing the client from re‑setting the deadline and extracting other users’ deposits.

## Proof of Concept
1. Navigate to contract [Shelter.sol](https://github.com/code-423n4/2022-02-concur/blob/main/contracts/Shelter.sol)
2. Observe that token can only be deactivated if activated[_token] + GRACE_PERIOD > block.timestamp. We will bypass this
3. onlyClient activates a token X using the activate function
4. Assume Grace period is crossed such that activated[_token] + GRACE_PERIOD < block.timestamp
5. Now if onlyClient calls deactivate function, it fails with “too late”
6. But onlyClient can bypass this by calling activate function again on token X which will reset the timestamp to latest in activated[_token] and hence onlyClient can now call deactivate function to disable the token and retrieve all funds present in the contract to his own address

## Recommendation
Add below condition to activate function:
```solidity
function activate(IERC20 _token) external override onlyClient {
    require(activated[_token]==0, "Already activated");
    activated[_token] = block.timestamp;
    savedTokens[_token] = _token.balanceOf(address(this));
    emit ShelterActivated(_token);
}
```
The warden has identified a way for the client to trick the shelter into sending all tokens to the client, effectively rugging all other users.

Because this is contingent on a malicious client, I believe Medium Severity to be more appropriate.
