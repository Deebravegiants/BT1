# [M] fees calculations are not accurate

## Summary
Severity: Medium
Contest weight: 0.1737
Dataset id: 1267
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from an inaccurate fee accounting mechanism that mints new tokens to represent the fee owed to a designated feeBeneficiary. The contract calculates the fee amount based on the current total supply of basket tokens and the value of the underlying assets, then mints exactly that number of new tokens to the feeBeneficiary. Because minting increases the total supply, the newly minted fee tokens represent a smaller proportion of the underlying asset pool than intended. For example, if the basket assets are worth $1,000,000 and the totalSupply is 1,000,000 tokens, a 10% fee should correspond to $100,000. The contract mints 100,000 new tokens, raising the totalSupply to 1,100,000. The feeBeneficiary now holds 100,000 of 1,100,000 tokens, which entitles them to only about $90,909 of underlying assets, shortchanging them by roughly 9% of the expected fee. This mis‑calculation occurs whenever fees are paid by minting additional tokens rather than by transferring existing value, and it is especially problematic when the feeBeneficiary also receives fees on its own fee holdings, causing compounded dilution. The impact is that the protocol systematically under‑pays the feeBeneficiary, leading to reduced revenue for the entity that funds protocol maintenance or profit sharing. Users may notice that expected payouts, refunds or fee disbursements are lower than advertised, seeing balances that appear correct in token units but translate to less underlying value. The issue was discovered during a manual audit that compared the theoretical fee amount with the actual value received after minting, revealing a discrepancy in the accounting logic. Because the bug manifests only after token minting, it can be subtle and may not produce obvious on‑chain errors; the token balances still appear consistent, masking the underlying loss of value. The fix requires redesigning the fee distribution to either mint a proportionally larger number of tokens that preserves the intended value share, or to transfer existing assets instead of minting, and to adjust the fee calculation to account for the increase in totalSupply caused by the minting operation. In essence, the contract should treat fees as a value transfer rather than a simple token mint, ensuring that the feeBeneficiary receives the exact monetary amount calculated, thereby preserving the accounting invariants of the basket token system.

## Proof of Concept
let’s assume that the basket assets are worth 1M dollars, and totalSupply = 1M. the result of `calcOutStandingAnnualizedFee` is 100,00 so the feeBeneficiary should get 100,00 dollars. however, when minting 100,00 the totalSupply will increase to 1,100,000 so they will own 100000/1100000 * (1M dollars) = 90909.09 dollars instead of 100k

This is mitigated by the feeBeneficiary diluting his own shares if he gets fees on his fees.

I’m not exactly sure if I understand what the warden is stating here. Could you confirm @loki-sama ?

Ok, I myself misunderstood. He is correct that we don’t get the full value. When we take a fee of 10% like from his example. What we do is mint 10% of the basket to ourselves. That 10% after minting is not holding 10% of the underling.

## Recommendation
No recommendation
