# [H] Vault rewards can be gamed

## Summary
Severity: High
Contest weight: 0.3714
Dataset id: 301
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `_deposit` function increases the member’s _weight_ by `_weight = iUTILS(UTILS()).calcValueInBase(iSYNTH(_synth).TOKEN(), _amount);` which is the swap output amount when trading the deposited underlying synth amount.

Notice that anyone can create synths of custom tokens by calling `Pools.deploySynth(customToken)`.

Therefore an attacker can deposit valueless custom tokens and inflate their member weight as follows:

  1. Create a custom token and issue lots of tokens to the attacker
  2. Create synth of this token
  3. Add liquidity for the `TOKEN <> BASE` pair by providing a single wei of `TOKEN` and `10^18` BASE tokens. This makes the `TOKEN` price very expensive.
  4. Mint some synths by paying BASE to the pool
  5. Deposit the fake synth, `_weight` will be very high because the token pool price is so high.

Call `harvest(realSynth)` with a synth with actual value. This will increase the synth balance and it can be withdrawn later.

Anyone can inflate their member weight through depositing a custom synth and earn almost all vault rewards by calling `harvest(realSynth)` with a valuable “real” synth. The rewards are distributed pro rata to the member weight which is independent of the actual synth deposited.

The `calcReward` function completely disregards the `synth` parameter which seems odd. Recommend thinking about making the rewards based on the actual synths deposited instead of a “global” weight tracker. Alternatively, whitelist certain synths that count toward the weight, or don’t let anyone create synths.

This is a valid attack path.

The counter is two fold:

  1. In the vault, `require(isCurated(token))` this will only allow synths of curated tokens to be deposited for rewards. [The curation logic ](https://github.com/code-423n4/2021-04-vader/blob/main/vader-protocol/contracts/Router.sol#L234) does a check for liquidity depth, so only deep pools can become synths. Thus an attacker would need to deposit a lot of BASE.
  2. In the vaults, use `_weight = iUTILS(UTILS()).calcSwapValueInBase(iSYNTH(_synth).TOKEN(), _amount);`, which computes the weight with respect to slip, so a small manipulated pool cannot be eligible. The pool would need to be deep.

The Vault converts all synths back to common accounting asset - USDV, so member weight can be tracked.

**[strictly-scarce (vader) commented](https://github.com/code-423n4/2021-04-vader-findings/issues/222#issuecomment-830635200):** Disagree with severity, since the daily rewards can be claimed by anyone in a fee-bidding war but no actual extra inflation occurs.

Severity: 2

## Recommendation
No recommendation
