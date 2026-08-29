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
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1437_
