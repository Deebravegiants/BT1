# [M] Epoch timeline is not strictly enforced on-chain

## Summary
Severity: Medium
Reporter: berndartmueller
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L234-L250
Type: audit-issue

## Details
# Epoch timeline is not strictly enforced on-chain

## Summary

Epoch timeline is not enforced on-chain and can be maliciously or accidentally manipulated by the off-chain keeper node.

## Vulnerability Detail

According to the specs, an epoch is a series of operations that occur on a strict 7-day schedule. Epoch operations, auction initialization, epoch initialization, and auction processing are handled by an authorized keeper address.

1. Auction initialization - Thursday at ~8 am UTC - `initializeAuction`
2. Epoch initialization - Friday at ~8 am UTC - `initializeEpoch`
3. Auction processing - Friday at ~12 pm UTC - `processAuction`

However, the epoch initialization and the auction processing operation are not strictly enforced on-chain to happen on the exact day and time. The keeper address can call these functions at any time. As the keeper is an off-chain node, it is possible that the keeper is not running at the exact time of the epoch operation or that the request, for any reason, is retried. This leads to an epoch being initialized earlier or later than expected.

## Impact

Epoch operations are not strictly enforced to happen on the exact day and time. Epochs can be initialized immediately after the previous epoch has been initialized.

## Code Snippet

[vault/VaultAdmin.initializeEpoch](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L234-L250)

```solidity
function initializeEpoch() external onlyKeeper {
    VaultStorage.Layout storage l = VaultStorage.layout();

    // skips epoch 0 as there will be no net income, and the lastTotalAsset balance
    // will not be set
    if (l.epoch > 0) _collectPerformanceFee(l);

    // when the queue processes its deposits, it will send the enitre balance to
    // the vault in exchange for a pro-rata share of the vault tokens.
    l.Queue.processDeposits();

    // increment the epoch id
    l.epoch = l.epoch + 1;

    // sets the max/min auction prices
    _setAuctionPrices(l);
}
```

[vault/VaultAdmin.processAuction](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L259-L338)

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
                totalCollateralUsed + _totalReserves()
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

Consider enforcing the epoch timeline on-chain by adding appropriate timestamps to the `Epoch` struct and checking them in the various functions.
