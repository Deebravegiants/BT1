# [M] Certain ERC-20 tokens will break auction processing

## Summary
Severity: Medium
Reporter: berndartmueller
Source: https://github.com/Premian-Labs/premia-contracts/blob/master/contracts/pool/PoolInternal.sol#L1341.
Type: audit-issue

## Details
# Certain ERC-20 tokens will break auction processing

## Summary

Some ERC-20 tokens require first setting the token allowance to `0` before setting it to a non-zero value. This is not the case in the `VaultAdmin.processAuction` function, therefore, if one of those affected tokens is used, auctions processing will fail.

## Vulnerability Detail

During the auction processing, the `VaultAdmin.processAuction` function will call `ERC20.approve` to approve the Premia pool to spend funds. However, some ERC-20 tokens, like USDT ([see line 199](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7#code)) or KNC ([see line 154](https://etherscan.io/token/0xdd974d5c2e2928dea5f71b9825b8b646686bd200#code#code)), require first reducing the address allowance to 0 and then approve the actual allowance. Otherwise, the approve function will revert and the auction processing will fail.

Currently, Premia does not use any of these affected tokens. However, if Premia decides to add one of these tokens in the future, the auction processing will fail and the `VaultAdmin` facet has to be upgraded.

It seems Premia does not necessarily spend the total allowance - see https://github.com/Premian-Labs/premia-contracts/blob/master/contracts/pool/PoolInternal.sol#L1341. Therefore it's possible to have a leftover allowance.

## Impact

Auctions can not be processed.

## Code Snippet

[vault/VaultAdmin.sol#L300-L303](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L300-L303)

```solidity
function processAuction() external onlyKeeper {
    VaultStorage.Layout storage l = VaultStorage.layout();

    // stores the last total asset amount, this is effectively the amount of assets held
    // in the vault at the start of the auction
    l.lastTotalAssets = _totalAssets();

    uint64 lastEpoch = _lastEpoch(l);
    VaultStorage.Option memory lastOption = _lastOption(l);

    uint256 totalCollateralUsed;
    uint256 totalPremiums;

    bool cancelled = l.Auction.isCancelled(lastEpoch);
    bool finalized = l.Auction.isFinalized(lastEpoch);

    require(
        (!finalized && cancelled) || (finalized && !cancelled),
        "auction is not finalized nor cancelled"
    );

    if (finalized && !cancelled) {
        // transfers the premiums from the auction contract to the vault
        totalPremiums = l.Auction.transferPremium(lastEpoch);
        //fetches the total number of contracts sold during the auction
        uint256 totalContractsSold =
            l.Auction.getTotalContractsSold(lastEpoch);

        if (totalContractsSold > 0) {
            // calculates the total amount of collateral required to underwrite the contracts
            // sold during the auction
            totalCollateralUsed = totalContractsSold
                .fromContractsToCollateral(
                l.isCall,
                l.underlyingDecimals,
                l.baseDecimals,
                lastOption.strike64x64
            );

            // approves the Premia pool to spend, the collateral amount + the reserves needed
            // to pay the APY fee
            ERC20.approve(
                address(Pool),
                totalCollateralUsed + _totalReserves() // @audit-info Some ERC-20 tokens revert if there's leftover allowance
            );

            // underwrites the contracts sold during the auction, the pool sends the short tokens
            // to the vault, and long tokens to the auction contract
            Pool.writeFrom(
                address(this),
                address(l.Auction),
                lastOption.expiry,
                lastOption.strike64x64,
                totalContractsSold,
                l.isCall
            );

            // the divestment timestamp is the time at which collateral locked in the Premia pool
            // will be moved into the pools "reserved liquidity" queue. if the divestment timestamp
            // is not set, collateral will remain in the "free liquidity" queue and could potentially
            // be used to underwrite a position without the directive of the vault. note, the minimum
            // amount of time the divestment timestamp can be set to is 24 hours after the position
            // has been underwritten.
            uint64 divestmentTimestamp = uint64(block.timestamp + 24 hours);
            Pool.setDivestmentTimestamp(divestmentTimestamp, l.isCall);
        }

        l.Auction.processAuction(lastEpoch);
    }

    // deactivates withdrawal lock
    l.auctionProcessed = true;

    emit AuctionProcessed(
        lastEpoch,
        totalCollateralUsed,
        _totalShortAsContracts(),
        totalPremiums
    );
}
```

## Tool Used

Manual review

## Recommendation

Consider using `ERC20.approve(address(Pool), 0)` before to ensure that the allowance is set to 0 before setting the actual amount.
