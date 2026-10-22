# [H] Missing access control in admin_withdraw_all_swap_fee operation

## Summary
Severity: High
Reporter: 0xluk3, also found by 0xlookman, metaldragon, timeless, 0xAadhi, trachev, chupinexx, undeﬁned, tinnohoﬃcial, 0xabdullah,
Contest weight: 0.4278
Dataset id: 4927
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
While the admin_withdraw_swap_fee is protected by the aforementioned operator
hook in src/contracts/common/auth.rell, the admin_withdraw_all_swap_fee has no such protection, de-
spite its similar administrative purpose.
Aside of the impact of this issue, there's additional inconsistency in the code and documentation: the func-
tion is preﬁxed with "admin_" suggesting it should be admin-only, but on the other hand, the comments
describe it as being for "an authenticated user" but also there is a note about "necessary permissions".
Regardless the description, this function's purpose is to transfer fees from the Uniswap treasury to the
staking treasury, which directly impacts the exchange rate for staked tokens. Any authenticated user can:
• Stake a large amount of tokens in the staking contract.
• Call admin_withdraw_all_swap_fee to transfer accumulated fees to the staking treasury.
• Capture the resulting value increase (as the staking contract's exchange rate appreciates).
• Immediately unstake to realize proﬁts.
This attack could drain value from legitimate long-term stakers who should be the intended recipients of
these fees. If ﬂash loans are implemented in the future, this attack could be executed with no upfront
capital, further amplifying the risk.

Impact Explanation:
Medium -- users may abuse this mechanism to stake opportunistically, draining
other users off their yield, however, this leads to capturing only part of the yield, which is a moderate
funds loss.

## Proof of Concept
Consider following attack ﬂow:
• There's some fees accumulated over time in the Uniswap treasury.
• Alice stakes a large amount of tokens, which may be even borrowed for this opportunity.
• Alice immediately calls admin_withdraw_all_swap_fee().
• Alice unstakes right after and receives more funds than staked since per design the value of xtokens
appreciated by the received yield from fees.
• Alice made proﬁt by opportunistic staking. Other users who stake fairly receive less from that reward
distribution batch, as at time of distribution, Alice had a major share of the total pool.

## Recommendation
Add proper admin or operator veriﬁcation to match the protection on admin_with-
draw_swap_fee. Consider making the function naming and documentation consistent with its intended
permission level to avoid future confusion. A lockup period on staking might prevent such abuses, but it
also changes the design of the contract, which may not be desired from business standpoint.
