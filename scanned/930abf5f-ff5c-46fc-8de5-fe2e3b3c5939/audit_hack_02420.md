# [H] Use of send

## Summary
Severity: High
Source: https://github.com/Superdao-DAO/Superdao-Seed-Stage1/blob/c20d6d45d911f59003122d97df701848cf597cab/contracts/PromissoryToken.sol#L291
Type: audit-issue

## Details
Use of `send` is always risky and should be analyzed in detail. One occurrence found in [line 291 of PromissoryToken.sol](https://github.com/Superdao-DAO/Superdao-Seed-Stage1/blob/c20d6d45d911f59003122d97df701848cf597cab/contracts/PromissoryToken.sol#L291).  
– [Always check send return value](https://medium.com/zeppelin-blog/onward-with-ethereum-smart-contract-security-97a827e47702#c528): OK.  
– [Consider calling send at the end of the function](https://medium.com/zeppelin-blog/onward-with-ethereum-smart-contract-security-97a827e47702#3d17): OK.  
– [Favor pull payments over push payments](https://medium.com/zeppelin-blog/onward-with-ethereum-smart-contract-security-97a827e47702#fa61): Severe problem.

If there is more than one destination in a withdrawal proposal, one of the destination addresses can prevent all others from getting the funds. If one of the destination addresses throws in the fallback function, the whole `approveWithdraw`function call will fail, causing all payments to fail. This gives control to any malicious payee to block payments to all other payees.

For more info on this problem, [see this note](https://github.com/ConsenSys/Ethereum-Development-Best-Practices/wiki/Fallback-functions-and-the-fundamental-limitations-of-using-send%28%29-in-Ethereum-&-Solidity#abuse).
