# [M] M-13 | Exposure During Closure Unaccounted

## Summary
Severity: Medium
Contest weight: 0.2765
Dataset id: 170
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the initiation of a close action, the position, or the portion of a position being removed, is effectively removed from the protocol as it is deducted from its corresponding tick and the cumulative balance and exposure accounting. However the USDN vault still serves as a counterparty for any PnL realized by the position in the period: [initiateClose, validateClose] and the user is still exposed to this price action as well. This may present an issue as the system will technically be more exposed to the long side than the imbalance tracking accounts for. As a result the corresponding imbalance mechanisms may not be used when they ought to.
Extracting value from a vault withdrawal (assuming 0 protocol fees):
1. Bob initiates close position. Bob provided empty Pyth data so Pyth.getPriceUnsafe() is called retrieving the price of Ether 59 minutes ago (price manually updated on-chain by Bob 59 minutes ago). The price retrieved is 1750 even though the current Ether price is 59 minutes later/now 1925. 14 minutes passes and Bob has not validated yet.
2. Alice initiates a withdrawal providing the actual current Pyth price of (1925 Ether price). We are assuming a 10% increment of Ether price in 1 hour 14 minutes.
3. Bob validates its position closure, and balanceVault is decreased based on the size of the long position closed and on the 10% price increase.
4. Alice validates withdrawal, but she still gets the assets respective to the vaultBalance at the time of the initiation. As the vaultBalance was higher, Alice unfairly gets more assets than she deserves. As at minute 60 + 14 the position value of Bob was already determined (it was already determined at minute 60 + 24 seconds) but Bob decided to delay his validation and because of this Alice received a higher amount of assets.
assetsReceivedWithExploit ................................... 1821845730818816586
assetsReceivedWithoutExploit ................................ 1813360204002626022
Increment of ................................................ 46794/10000000 (0.47%)
Value of the position closed compared to total long value ... 2%
Price change ................................................ 10% increment of Ether price
Extracting value from a vault deposit (assuming 0 protocol fees):
1. Bob initiates close position. Bob provided empty Pyth data so Pyth.getPriceUnsafe() is called retrieving the price of Ether 59 minutes ago (price manually updated onchain by Bob 59 minutes ago). The price retrieved is 1750 even though the current Ether price is 59 minutes later/now 1575. 14 minutes passes and Bob has not validated yet.
2. Alice initiates a deposit providing the actual current Pyth price of (1575 Ether price). We are assuming a 10% decrement of Ether price in 1 hour 14 minutes.
3. Bob validates its position closure, and balanceVault is increased based on the size of the long position closed and on the 10% price decrease.
4. Alice validates her deposit, but she still gets the shares respective to the vaultBalance at the time of the initiation. As the vaultBalance was lower, Alice unfairly gets more shares than she deserves. As at minute 60 + 14 the position value of Bob was already determined (it was already determined at minute 60 + 24 seconds) but Bob decided to delay his validation and because of this Alice received a higher amount of shares.
sharesReceivedWithExploit ...................................
sharesReceivedWithoutExploit ................................
Increment of ................................................ 45872/10000000 (0.46%)
Value of the position closed compared to total long value ... 2%
Price change ................................................ 10% decrement of Ether price

## Recommendation
Consider introducing specific accounting in the imbalance calculations for the exposure of all position amounts which have been effectively closed after initiation, but have yet to be validated and have their exposure officially removed. If this approach is taken, then one inconsistency should be addressed. When an individual liquidation occurs during a close action validation, the position is valued at the block in which the action was initiated, however this contradicts the logic that follows for a normal close, where the vault is exposed to the current value of the position.
These two scenarios should be standardized in terms of exposure. If the first suggestion is implemented, the liquidations should be adjusted to also have exposure to the latest asset price. Alternatively, the exposure over the period [initiateClose, validateClose] could be removed entirely, and the exact position value to be realized could be computed during the initiation.
