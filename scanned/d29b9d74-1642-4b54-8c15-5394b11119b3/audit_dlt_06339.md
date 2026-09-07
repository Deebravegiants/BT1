# [H] Deposit is broken for tokens that transfer the max balance of user on max transfer of uint256.max, which can lead to loss of fund to protocol

## Summary
Severity: High
Chain: Smart contract
Component: Blast-Futures-Exchange
Published: 2024-02-05
Source: https://github.com/hats-finance/Blast-Futures-Exchange-0x97895c329b950755566ddcdad3395caaea395074/issues/28
Type: hats-finding

## Details
**Github username:** @0xnirlin
**Twitter username:** 0xnirlin
**Submission hash (on-chain):** 0x82df74b8462469f3a531103b93d52a6cf29e72e7849a611d885026c9f5594a7f
**Severity:** high

**Description:**
**Description**\
There are some tokens, that on transferring uint256.max amount of tokens, instead of reverting in case the user doesn't hold that amount of balance, transfers the whole user balance.

So in case the underlying token is cUSDCv3, which is not a low market cap token so possibility of it being used is pretty good.

The market cap of cUSDCv3 at the time of submission is $139,433,046

Reference from here : https://www.coingecko.com/en/coins/compound-usd-coin

Example:  if the user has approved uint256.max to the contract but has 100 tokens, and the contract tries to transfer uint256.max tokens from the user it will receive 100 tokens, but the accounting will believe the user has transferred uint256.max tokens. 

**Attachments**
Look at the following submission in one of Sherlock's contests that is similar to the current case

https://github.com/sherlock-audit/2023-09-Gitcoin-judging?tab=readme-ov-file#issue-m-8-problems-with-tokens-that-transfer-less-than-amount-separate-from-fee-on-transfer-issues

1. **Proof of Concept (PoC) File**
In our case, the deposit function looks like the following 

```solidity
    function deposit(uint256 amount) external nonReentrant {
        bool success = makeTransferFrom(msg.sender, address(this) , amount);
        require(success, "TRANSFER_FAILED");
        uint256 depositId = allocateDepositId();
        emit Deposit(depositId, msg.sender, amount);
    }
```

which means that if a token like cUSDCv3) is being used that contains a special case for amount == type(uint256).max in their transfer functions it results in only the user's balance being transferred.

This means that a user can deposit as low as 1 wei but the off-chain nodes will catch if the user deposits a very large amount as the function emits the user passed-in amount value that will be uin256.max.


_Trimmed to 38 lines — full report: https://github.com/hats-finance/Blast-Futures-Exchange-0x97895c329b950755566ddcdad3395caaea395074/issues/28_
