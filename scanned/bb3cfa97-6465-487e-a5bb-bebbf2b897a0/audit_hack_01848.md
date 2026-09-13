# [H] Whitelisted tokens limit

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

`_ragequit` function is iterating over all whitelisted tokens:


**contracts/Moloch.sol:L507-L513**
```solidity
for (uint256 i = 0; i < tokens.length; i++) {
    uint256 amountToRagequit = fairShare(userTokenBalances[GUILD][tokens[i]], sharesAndLootToBurn, initialTotalSharesAndLoot);
    // deliberately not using safemath here to keep overflows from preventing the function execution (which would break ragekicks)
    // if a token overflows, it is because the supply was artificially inflated to oblivion, so we probably don't care about it anyways
    userTokenBalances[GUILD][tokens[i]] -= amountToRagequit;
    userTokenBalances[memberAddress][tokens[i]] += amountToRagequit;
}
```

If the number of tokens is too big, a transaction can run out of gas and all funds will be blocked forever. Ballpark estimation of this number is around 300 tokens based on the current OpCode gas costs and the block gas limit. 

#### Recommendation

A simple solution would be just limiting the number of whitelisted tokens.

If the intention is to invest in many new tokens over time, and it's not an option to limit the number of whitelisted tokens, it's possible to add a function that removes tokens from the whitelist. For example, it's possible to add a new type of proposals, that is used to vote on token removal if the balance of this token is zero.  Before voting for that, shareholders should sell all the balance of that token.
