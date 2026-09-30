# [H] Yield of `LiquidityReserve` can be stolen

## Summary
Severity: High
Contest weight: 0.3880
Dataset id: 13088
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the way the LiquidityReserve contract distributes the fees that accrue from unstaking operations. When a user invokes instantUnstakeReserve(), the protocol immediately calculates a fee, adds it to the total locked value and distributes the resulting yield across all liquidity providers by crediting their share balances. Because the contract permits any participant to add or remove liquidity in the same block without incurring a penalty, an attacker can perform a Just‑In‑Time (JIT) liquidity sandwich around the instantUnstakeReserve() call. The attacker fronts‑runs the legitimate transaction by borrowing a large amount of the staking token, adding liquidity just before the victim’s instantUnstake, then lets the fee be credited to the enlarged liquidity pool, and finally removes the liquidity after the fee distribution, repaying the loan and pocketing a disproportionate share of the fee. This sequence allows the attacker to siphon the yield that should have been shared among honest liquidity providers. The root cause is the combination of (1) immediate, block‑level fee distribution and (2) the absence of any lock‑up period or withdrawal fee for liquidity added to the reserve. The exploit is possible only when an instantUnstakeReserve() transaction is observed, making the attack opportunistic but potentially highly profitable for large‑scale actors. From a user perspective the symptom is that liquidity providers see their expected fee earnings disappear or become significantly lower; a provider may notice that after adding liquidity they receive no increase in share value despite other users unstaking. The protocol itself suffers because the economic incentive for providing liquidity erodes, undermining the design that relies on fee sharing to reward LPs. No direct loss of user funds occurs, which can make the issue subtle and easy to miss during functional testing. The flaw belongs to the class of economic front‑running or sandwich attacks caused by missing time‑weighted accounting and unrestricted liquidity mutability. Mitigation strategies include deferring fee distribution across several blocks, imposing a small withdrawal fee, and enforcing a lock‑up period (e.g., prohibiting withdrawals for X blocks after liquidity addition). These measures raise the cost of the sandwich and make it unprofitable, restoring confidence that liquidity providers will receive the fees they are supposed to earn.

## Proof of Concept
The yield of `LiquidityReserve` is distributed when a user calls `instantUnstakeReserve()` in `Staking`. Then, in `instantUnstake`, `totalLockedValue` increases with the fee paid by the user withdrawing. The fee is shared between all liquidity providers as they all see the value of their shares increase.

Therefore, an attacker could do the following sandwich attack when spotting a call to `instantUnstakeReserve()`.

* In a first tx before the user call, borrow a lot of `stakingToken` and `addLiquidity`
* The user call to `instantUnstakeReserve()` leading to a fee of say `x`
* In a second tx after the user call, `removeLiquidity` and repay the loan, taking a large proportion of the user fee

The problem here is that you can instantly add and remove liquidity without penalty, and that the yield is instantly distributed.

## Recommendation
To mitigate this, you can

* store the earned fees and distribute them across multiple blocks to make sure the attack wouldn’t be worth it
* add a small fee when removing liquidity, which would make the attack unprofitable
* prevent users from withdrawing before X blocks or add a locking mechanism

This is not unique to the protocol and is a vulnerability in almost all of the LP designs that are prevalent today. There is no loss of user funds here either.

Would downgrade to Low or QA.

In standard cases of JIT, for example in a DEX, the attacker takes a risk as the liquidity he adds is used during the swap, and this liquidity is useful for the protocol as leads to a better price for the user, which is not the case here

@Picodes - that is fair but the liquidity is still useful and I still don’t see how this qualifies as high severity. Eventually it would mean that the liquidity reserve would need less liquidity parked in it if JITers always where hitting it.

To me it’s high because: (correct me if I am missing things)

* JIT is not useful here at all for the protocol, the liquidity they bring is not useful as does not get locked. It’s totally risk free, and as you said it’s a commun attack so it’s likely that someone uses it
* It leads to a loss of LP funds: Assume there is 100k unlocked in the pool, and someone `instantUnstake` 100k, it’ll lock all the LP liquidity. But if someone JITs this, the fees will go to the attacker and not the LP which provided the service by accepting to have its liquidity locked.
* From a protocol point of view, LPing becomes unattractive as all the fees are stolen, breaking the product design

Agree going to leave this as high. Any whale that does a large unstake will be susceptible to having more of the fee’s eroded to a predatory sandwich attack which provides no value to the system.
