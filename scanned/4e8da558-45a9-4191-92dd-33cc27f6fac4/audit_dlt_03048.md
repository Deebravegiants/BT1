# [M] LidoETHStrategy buys stETH at 1-1 instead of buying it from the Pool at Discount

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1437
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/lido/LidoEthStrategy.sol#L128-L137


# Vulnerability details

### Impact
In most cases stETH is always cheaper than ETH

See CL Oracle: https://data.chain.link/arbitrum/mainnet/crypto-eth/steth-eth

Reporting `0.999100` ETH / stETH


However, the strategy is always wrapping ETH to stETH by depositing it into the Lido Contract

https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/lido/LidoEthStrategy.sol#L128-L137

```solidity
        if (queued > depositThreshold) {
            require(!stEth.isStakingPaused(), "LidoStrategy: staking paused");
            INative(address(wrappedNative)).withdraw(queued);
            stEth.submit{value: queued}(address(0)); //1:1 between eth<>stEth // TODO: Prob cheaper to buy stETH
            emit AmountDeposited(queued);
            return;
        }
```

This means that the Strategy is inherently taking some loss (ETH price vs stETH price) on each deposit

### POC
Compare the Realized value from depositing against the price shown by the feeds

Here's the last two weeks data I scraped from onChain:

```
| roundId              | answer             | As ETH       | LOSS IN BPS | startedAt  | updatedAt  | answeredInRound      |
| -------------------- | ------------------ | ------------ | ----------- | ---------- | ---------- | -------------------- |
| 18446744073709551726 | 998550934081305700 | 0.9985509341 | 14.49065919 | 1687725027 | 1687725027 | 18446744073709551726 |
| 18446744073709551761 | 9.98847E+17        | 0.99884668   | 11.5332     | 1690749851 | 1690749851 | 18446744073709551761 |
| 18446744073709551730 | 998958688800485800 | 0.9989586888 | 10.413112   | 1688070676 | 1688070676 | 18446744073709551730 |
| 18446744073709551732 | 998988324489792200 | 0.9989883245 | 10.1167551  | 1688243534 | 1688243534 | 18446744073709551732 |
| 18446744073709551733 | 998988336918386800 | 0.9989883369 | 10.11663082 | 1688329961 | 1688329961 | 18446744073709551733 |
| 18446744073709551724 | 999064611648799700 | 0.9990646116 | 9.353883512 | 1687552189 | 1687552189 | 18446744073709551724 |
| 18446744073709551743 | 9.99093E+17        | 0.99909267   | 9.0733      | 1689194182 | 1689194182 | 18446744073709551743 |
```

Full 2 Weeks Dataset:
https://docs.google.com/spreadsheets/d/1iPEuOtCHt39GkeO-R-y1EyFMxKJbNKS-8ze3WqdiVLk/edit?usp=sharing

As you can see, the strategy is locking in a loss of up to 15 BPS just in depositing

Since the Swap Fee on Mainnet is 1 BPS this is 15 times more than necessary

If we consider earlier times, it's not uncommon for stETH to have higher price changes

### Mitigation

Check the pool and see if it's cheaper to buy stETH from it

Or refactor the code to only use stETH which avoids single sided exposure which creates further issues in the strategy

### Additional Resources

The historical CL prices:
https://docs.google.com/spreadsheets/d/1PZKBAV7rhxJBa4xKwnobTt8KpauLOK31RLnHTGB4JO8/edit?usp=sharing

As you can see stETH has had periods of wild fluctuations the highest in 2023 reaching a Depeg of over 1%
`131.7212195 BPS`



## Assessed type

Oracle
