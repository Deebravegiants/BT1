# [H] In `ERC20`, `TotalSupply` is broken

## Summary
Severity: High
Contest weight: 0.2139
Dataset id: 10200
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns an accounting flaw in an ERC‑20 implementation where the contract’s total supply variable is not correctly initialized before token minting. The constructor accepts a parameter (often called _initialSupply) and additionally mints the same amount of tokens, but the internal _totalSupply counter is left at its default uninitialized value instead of being set to zero. As a result, the totalSupply() view returns a value that includes both the initial parameter and the minted amount, effectively double‑counting the supply. This happens whenever the contract is deployed with a non‑zero initial supply and later any minting operation is performed. The bug is discovered during a security audit (Code4rena) by inspecting the constructor logic and noticing that the totalSupply returned 1000 immediately after deployment with an initialSupply of 1000, and grew to 2000 after minting another 1000 tokens, which contradicts the expected accounting where totalSupply should match the exact number of tokens minted. Exploitation does not require a malicious attacker; the incorrect totalSupply value can be observed by any user or third‑party service that queries the token contract. Because many DeFi protocols, market‑cap calculators, price oracles and analytics dashboards rely on the totalSupply value to compute ratios, liquidity, or governance thresholds, the inflated number can lead to wrong market‑cap calculations, mis‑allocation of rewards, and faulty governance decisions. From a user’s perspective the symptom is that the token explorer or wallet UI displays a total supply that is higher than the amount of tokens circulating, and expectations that a 1000‑token deployment should show 1000 are violated – the UI may show 2000 after a single mint. The issue belongs to the class of "incorrect accounting" or "state initialization" bugs, where a storage variable is left in an undefined state and later updated in a way that does not reflect the intended invariant. It can be hard to notice because the contract still allows minting and transfers, and the discrepancy appears only in the totalSupply view, which may not be directly exercised in functional tests. The conceptual fix is to ensure that the totalSupply counter is initialized to zero in the constructor before any minting, or to eliminate the redundant initialSupply parameter and rely exclusively on the mint function to set the correct supply. By resetting the counter or removing the extra parameter, the totalSupply function will faithfully reflect the true amount of tokens minted, restoring correct accounting for downstream integrations.

## Proof of Concept
If the constructor is called with `_initialSupply = 1000`, then `1000` tokens are minted. The total supply will be `2000`.

## Recommendation
Remove `_initialSupply`.

The explanation is not clear. We can’t seem to reproduce this issue as we can’t find a scenario where the `totalSupply` function returns an incorrect value.

@tkkwon1998 to clarify:

Deploy the ERC20 with `totalSupply_ = 1000`.

Then `totalSupply()` returns 1000, which is incorrect.

Then if someone mints 1000 tokens, there is 1000 tokens in the market but due to `_totalSupply += amount;`, totalSupply = 2000 which is still incorrect

I believe the submission could have benefitted by:

  * A coded POC
  * Recognizing a revert due to the finding


However the finding is ultimately true in that, because `totalSupply` is a parameter passed in to the contract, and the ERC20 contract will not mint that amount, the `totalSupply` will end up not reflecting the total amounts of tokens minted.

For this reason, I believe the finding to be valid and High Severity to be appropriate.

I recommend the warden to err on the side of giving too much information to avoid getting their finding invalidated incorrectly.

After further thinking, I still believe the finding is of high severity as the ERC20 standard is also broken. I do believe the submission could have been better developed, however, I think High is in place here.
