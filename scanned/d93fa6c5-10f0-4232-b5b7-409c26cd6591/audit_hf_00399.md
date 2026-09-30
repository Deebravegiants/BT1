# [M] Wrong handling of wallet open

## Summary
Severity: Medium
Contest weight: 0.2476
Dataset id: 1785
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Wrong handling of wallet open interest will cause issues Not properly handling wallet open interest per each pair. Each wallet can have a certain amount of max interest (the code below is a check in TradingStorage::withinExposureLimits() that must hold true when opening a trade): walletOI(_trader) + _leveragedPos <= pairsStored.maxWalletOI(_pairIndex); The issue is that we are checking the total wallet open interest of a trader against the max wallet open interest for a particular pair. Let's take a look at PairStorage::maxWalletOI(): function maxWalletOI(uint _pairIndex) external view override returns (uint) { return (storageT.maxOpenInterest() * pairs[_pairIndex].values.maxWalletOI) / 100; ,→ } As seen, we calculate the max open interest for a wallet based on the pair index provided. For the walletOI function used in the check above, we can clearly see that there is no pair index input, thus we can see that the return value of the function is not based on the pair of the trade. Let's also take a look at TradingStorage::_updateOpenInterestUSDC() where the wallet open interest for a trader gets updated: _walletOI[_trader] = _open ? _walletOI[_trader] + _leveragedPosUSDC : _walletOI[_trader] - _leveragedPosUSDC; ,→ As seen, it gets updated the same way regarding of the pair index. From the docs, I could not deduct whether the intentions were for each pair to have its own max wallet OI or for there to be a max wallet OI across all pairs. Either way, the current implementation is wrong as it is a mixture of the 2. Internal pre-conditions External pre-conditions Attack Path 1. There are 2 pairs, each with a maximum open interest of 100 2. Bob creates a trade on one of the pairs with a position size of 100 3. His wallet open interest gets updated to 100 4. He tries to create another trade on the other pair with a position size of 100 5. This reverts as he already has 100 wallet open interest which is also the maximum wallet open interest for the other pair (despite him having 0 open trades on the other pair) Unexpected reverts

## Recommendation
Refactor the code to match your intention (either max wallet open interest for each pair or max wallet open interest across all pairs)
