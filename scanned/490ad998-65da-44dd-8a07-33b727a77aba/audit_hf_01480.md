# [M] Possible token reentrancy in release

## Summary
Severity: Medium
Contest weight: 0.3574
Dataset id: 7851
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a token‑reentrancy flaw in the release function of the BathBuddy contract. The function transfers vested bonus tokens to a beneficiary and only after the transfer updates an internal counter that records how many tokens have been released. If the bonus token implements a callback mechanism – for example an ERC777 token that invokes tokensReceived or a malicious ERC20 that includes a fallback‑style hook – the callback can call release again before the counter is updated. This re‑entrancy allows a malicious beneficiary to invoke the release logic repeatedly within a single transaction, retrieving the same vested amount multiple times and effectively bypassing the intended vesting schedule. The root cause is the absence of a re‑entrancy guard (such as a nonReentrant modifier or the contract’s synchronized modifier) and the violation of the checks‑effects‑interactions pattern: the state change (updating the released‑tokens counter) occurs after the external token transfer, giving the external contract control over execution flow. An attacker can craft a malicious token contract that, when received, executes tokensReceived or a fallback function which immediately calls release again. Because the release function does not prevent this recursive call, the loop continues until the full vested balance is drained, while other beneficiaries remain unaffected. From a user’s perspective the expected behaviour – waiting for the vesting period to elapse before receiving tokens – is broken; users may see their tokens arriving instantly, or conversely may observe that a beneficiary repeatedly calls release and the contract’s internal accounting shows zero remaining releases while the attacker’s balance grows. The issue was discovered during a security audit that inspected the contract’s token handling flow and compared it with other contracts that already employ a synchronization modifier. It is hard to notice because the external token contract appears to behave like a standard ERC20, and the re‑entrancy only manifests when the token implements a callback, a scenario that may not be covered by typical unit tests. The impact is functional rather than direct loss of other users’ funds: the protocol’s vesting guarantees are violated, undermining trust in the reward system. To remediate, the release function should be protected with a re‑entrancy guard and reordered to follow the checks‑effects‑interactions pattern – updating the released‑tokens counter before performing the external token transfer – or alternatively use a pull‑payment model that eliminates external calls during state changes. By applying these mitigations, the contract would prevent malicious tokens from regaining control of execution flow, ensuring that vesting periods are respected and that token releases cannot be replayed to siphon additional rewards.

## Proof of Concept
In the function release, [line](https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/peripheral_contracts/BathBuddy.sol#L87), there’s no modifier to stop reentrancy, in the other contracts it would be the synchronized modifier. If a token could reenter with a hook in a malicious contract (an ERC777 token, for example, which is backwards compatible with ERC20), released token [counter array](https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/peripheral_contracts/BathBuddy.sol#L116) wouldn’t be updated, enabling the withdrawal of the vested amount before the vesting period ends. A plausible scenario would be:

1. A malicious beneficiary contract B calls the release() function with itself as the recipient, everything goes according to the function, and transfer and callback to the malicious beneficiary contract happens.
2. Contract B contains tokensReceived(), a function in the ERC777 token that allows for callback to the victim contract as you can see here <https://twitter.com/transmissions11/status/1496944873760428058/> (This function also can be any function that is analogous to a fallback function that might be implemented in a modified ERC20. As it can be seen, any token that would give the attacker control over the execution flow will suffice.)
3. Inside the tokensReceived() function, a call is made back to the release function.
4. This steps are repeated until vested amount is taken back.
5. This allows for the malicious beneficiary contract to redeem the vested amount while bypassing the vesting period, due to the released token counter array (<https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/peripheral_contracts/BathBuddy.sol#L116>) which controls how many tokens are released (<https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/peripheral_contracts/BathBuddy.sol#L101>) being updated only after the transferring of all tokens occurs. As this is the case, malicious beneficiary can get the usual amount that they could withdraw at the time indefinite amount of times (as result of released in line 101 will be 0), thus approximately getting all of their vested amount back without waiting for the vesting period. (fees not included).

There’s also precedents of similar bugs that reported, as seen [here](https://github.com/code-423n4/2022-01-behodler-findings/issues/154#issuecomment-1029448627)

## Recommendation
1. Consider adding a mutex such as nonReentrant, or the synchronized modifier used in the other contracts.
2. Implement checks-effects-interactions pattern.

This one should probably be a high priority, adding disagreement with severity.

From what I gather, `bonusTokens` can be any ERC20 token (network incentives/governance tokens), which by extension, means ERC777 tokens are possible too.

Even if not, I suppose one could spin up a malicious bonus token to specifically target the BathBuddy contract. 

Medium severity because there isn’t a loss nor stolen rewards from others, merely bypassing the vesting, which is an impact on protocol functionality.  
`2 — Med: Assets not at direct risk, but the function of the protocol or its availability could be impacted, or leak value with a hypothetical attack path with stated assumptions, but external requirements.`
