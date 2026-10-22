# [H] 5.2.15ClearingHousecannot detect if a call fromSeaportcomes from a genuine listing or auction

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** ClearingHouse.sol#L21
**Description:** Anyone can create aSeaPortorder with one of the considerations' recipients set to aClearingHouse
with acollateralIdthat is genuinely already set for auction. Once the spoofed order settles,SeaPortcalls into
thisfallbackfunction and causes the genuine Astaria auction to settle.
This allows an attacker to set random items on sale onSeaPortwith funds directed here (small buying prices) to
settle genuine Astaria auctions on the protocol.
This causes:

- The Astaria auctionpayees and theliquidatorwould not receive what they would expect that should come
    from the auction. And ifpayeeis a public vault it would introduce incorrect parameters into its system.
- Lien data (s.lienMeta[lid]) and the lien token get deleted/burnt.
- Collateral token and data get burnt/deleted.
- When the actual genuine auction settles and calls back to here, it will revert due to
    s.collateralIdToAuction[collateralId]check.
**Recommendation:** Astaria needs to introduce a mechanism so thatSeaportwould send more data toClearing-
Houseto check the genuineness of the fallback calls.
**Astaria:** In a change yet to be merged, we have theClearingHousesetup with checks to enforce that it has
received enough of a payment in the right asset to complete the txn, we ultimately do not care where the txn came
from as long as we are indeed offering the payment, and are getting everything that the auction should cost. Will
mark it as acknowledged and tag this ticket with the updates when merged.
**Spearbit:** Acknowledged.
