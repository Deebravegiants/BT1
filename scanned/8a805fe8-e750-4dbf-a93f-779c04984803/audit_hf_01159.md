# [M] remove_liquidity performs incorrect validation

## Summary
Severity: Medium
Reporter: trachev, also found by 10xCriticals, ZanyBonzy, timeless, zubyoz and tinnohoﬃcial
Contest weight: 0.2835
Dataset id: 4942
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In order to make sure that a user does not receive less of tokenA and tokenB when withdrawing their liquidity remove_liquidity allows the caller to specify amount_a_min and amount_b_min.  
The withdrawn token amounts must never be less than the minimum values. Here is how the validation is currently performed:
```rell
if (token0 == asset_a) {
    amount_a = amount_0;
    amount_b = amount_1;
} else {
    amount_a = amount_1;
    amount_b = amount_0;
}
require(amount_0 >= amount_a_min, "UniswapV2Router: INSUFFICIENT_A_AMOUNT");
require(amount_1 >= amount_b_min, "UniswapV2Router: INSUFFICIENT_B_AMOUNT");
```
This, however, is an issue as when comparing the withdrawn amount to the minimum the protocol uses amount_0 and amount_1. Depending on the order of the assets amount_0 may actually point to the amount of token_b, which we can clearly see based on the if statement which re-orders the token amounts.  
Despite this, the function always compares amount_0 to amount_a_min and amount_1 to amount_b_min. This is problematic as the validation will either not correctly revert or revert incorrectly, preventing the user from removing their liquidity. For example:  
1. A user removes their liquidity, however, token0 is not equal to asset_a.  
2. Now amount_0 which represents the amount of token_b is compared to amount_a_min.  
3. token_b has 18 decimal places and token_a has 6 decimal places, therefore in almost cases amount_a_min will be lower than amount_0 allowing the removal of liquidity to execute successfully.  
4. This is problematic as a sandwich attack may have occurred, causing amount_0 to be much less than desired. The attack, however, will not be prevented by the slippage protection due to the incorrect validation.

Impact Explanation:  
The impact is High as users become vulnerable to sandwich attacks and risk losing their funds. On the other hand even without sandwich attacks the issue may cause users to be unable to withdraw their assets as the function can also revert when the actual amount would have been above the minimum but amount_0 returned a too low value.

## Proof of Concept
A proof of concept is normally required for Critical, High and Medium Submissions for reviewers under 80 reputation points. Please check the competition page for more details, otherwise your submission may be rejected by the judges.

## Recommendation
The correct implementation should be:
```rell
if (token0 == asset_a) {
    amount_a = amount_0;
    amount_b = amount_1;
} else {
    amount_a = amount_1;
    amount_b = amount_0;
}
require(amount_a >= amount_a_min, "UniswapV2Router: INSUFFICIENT_A_AMOUNT");
require(amount_b >= amount_b_min, "UniswapV2Router: INSUFFICIENT_B_AMOUNT");
```
