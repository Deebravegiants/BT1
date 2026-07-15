### Title
NFT Royalty Bypass via Integer Division Truncation in `compute_royalty_amount` - (File: chia/wallet/nft_wallet/nft_wallet.py)

### Summary
The `compute_royalty_amount` function in `chia/wallet/nft_wallet/nft_wallet.py` uses sequential integer floor division to compute NFT royalty amounts. When the offered amount is small relative to the royalty percentage, the result truncates to zero. When the royalty is zero, `make_nft1_offer` explicitly filters that trade price out of `trade_prices_list`, causing the CLVM royalty transfer program to receive an empty price list and enforce no royalty at all. An unprivileged taker can exploit this to transfer royalty-enabled NFTs while paying zero royalties to the creator.

### Finding Description
`compute_royalty_amount` applies two sequential floor divisions:

```python
# chia/wallet/nft_wallet/nft_wallet.py, line 64
amount = abs(offered_amount) // royalty_split * percentage // MAX_ROYALTY_BASIS_POINTS
```

For any `offered_amount` where `abs(offered_amount) // royalty_split * percentage < 10000`, the result is `0`. The existing test suite explicitly documents and accepts this behavior:

```python
# chia/_tests/wallet/nft_wallet/test_nft_royalty.py, line 42-44
def test_small_amount_truncates_to_zero() -> None:
    result = compute_royalty_amount(offered_amount=-50, royalty_split=1, percentage=100)
    assert result == uint64(0)
```

In `make_nft1_offer`, the `trade_prices_list` passed to the NFT singleton spend is filtered to exclude any price whose royalty would be zero:

```python
# chia/wallet/nft_wallet/nft_wallet.py, line 893-897
trade_prices_list=[
    list(price)
    for price in trade_prices
    if price[0] * offered_royalty_percentages[asset] // MAX_ROYALTY_BASIS_POINTS != 0
],
```

When `trade_prices_list` is empty, the CLVM royalty transfer program has no prices to enforce royalties against, so the NFT transfer completes with zero royalty paid.

The same truncation exists in the display-facing `royalty_calculation` static method:

```python
# chia/wallet/nft_wallet/nft_wallet.py, line 719
"amount": abs(amount) // len(royalty_assets_dict) * percentage // MAX_ROYALTY_BASIS_POINTS,
```

This means both the UI display and the actual spend bundle computation agree on zero royalty, so the maker sees no discrepancy in the offer summary.

### Impact Explanation
An unprivileged taker can structure an offer for a royalty-enabled NFT with a fungible amount small enough that `compute_royalty_amount` returns 0. The resulting spend bundle omits royalty payments entirely. The CLVM royalty transfer program enforces royalties only based on the `trade_prices_list` embedded in the spend; with an empty list, no royalty is enforced on-chain. The NFT creator (royalty recipient) receives zero royalty despite the NFT having a non-zero royalty percentage. This is an unauthorized accounting change affecting XCH or CAT amounts in NFT offer settlement.

The truncation threshold per NFT is: `offered_amount < MAX_ROYALTY_BASIS_POINTS / percentage`. For a 1% royalty (100 basis points), any offer below 100 mojos per NFT pays zero royalty. With `offer_side_royalty_split > 1` (multiple NFTs offered simultaneously), the per-NFT trade price is further divided before the royalty is computed (`amount // offer_side_royalty_split`), raising the effective bypass threshold proportionally.

### Likelihood Explanation
The attack requires the taker to offer a small enough fungible amount. For typical NFT trades this threshold is very low (sub-100 mojos for 1% royalty). However, with multiple NFTs in a single offer (`offer_side_royalty_split` large) or very low royalty percentages, the threshold rises. The attack is fully unprivileged: any taker can craft such an offer. The maker may accept because the displayed royalty summary (from `royalty_calculation`) also shows zero, masking the bypass.

### Recommendation
Replace the double floor-division with a single multiplication before division to minimize truncation:

```python
amount = abs(offered_amount) * percentage // (royalty_split * MAX_ROYALTY_BASIS_POINTS)
```

Additionally, add a guard that raises or warns when `percentage > 0` but the computed royalty is `0`, so callers are aware that the royalty has been truncated to zero rather than silently accepting it. The `trade_prices_list` filter should also be reviewed: filtering out zero-royalty prices silently removes on-chain enforcement rather than surfacing the truncation as an error.

### Proof of Concept
1. Alice mints an NFT with `royalty_percentage = 100` (1%) and lists it for sale.
2. Eve (taker) calls `respond_to_offer` offering `99` mojos of XCH for the NFT.
3. Inside `make_nft1_offer`, `compute_royalty_amount(-99, 1, 100)` computes `99 // 1 * 100 // 10000 = 9900 // 10000 = 0`.
4. `royalty_payments` contains a `CreateCoin` with `amount=0`; `payment_sum == 0`, so the royalty coin output is skipped entirely (line 911-912).
5. The `trade_prices_list` filter at line 896 also excludes the price because `price[0] * 100 // 10000 == 0`.
6. The NFT spend bundle is submitted with an empty `trade_prices_list`; the CLVM royalty transfer program enforces no royalty.
7. Eve receives the NFT; Alice receives 99 mojos and zero royalty. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** chia/wallet/nft_wallet/nft_wallet.py (L60-68)
```python
def compute_royalty_amount(offered_amount: int, royalty_split: int, percentage: int) -> uint64:
    """Compute royalty using integer arithmetic, validating against overflow and excessive percentage."""
    if percentage > MAX_ROYALTY_BASIS_POINTS:
        raise ValueError(f"NFT royalty percentage {percentage} exceeds 100% ({MAX_ROYALTY_BASIS_POINTS} basis points)")
    amount = abs(offered_amount) // royalty_split * percentage // MAX_ROYALTY_BASIS_POINTS
    royalty = uint64(amount)
    if royalty >= abs(offered_amount):
        raise ValueError("Royalty amount meets or exceeds the offered amount")
    return royalty
```

**File:** chia/wallet/nft_wallet/nft_wallet.py (L715-720)
```python
                summary_dict[id].append(
                    {
                        "asset": name,
                        "address": address,
                        "amount": abs(amount) // len(royalty_assets_dict) * percentage // MAX_ROYALTY_BASIS_POINTS,
                    }
```

**File:** chia/wallet/nft_wallet/nft_wallet.py (L893-897)
```python
                            trade_prices_list=[
                                list(price)
                                for price in trade_prices
                                if price[0] * offered_royalty_percentages[asset] // MAX_ROYALTY_BASIS_POINTS != 0
                            ],
```

**File:** chia/wallet/nft_wallet/nft_wallet.py (L909-912)
```python
                    # Skip it if we're paying 0 royalties
                    payments = royalty_payments[asset] if asset in royalty_payments else []
                    if sum(p.amount for _, p in payments) == 0:
                        continue
```

**File:** chia/_tests/wallet/nft_wallet/test_nft_royalty.py (L42-44)
```python
def test_small_amount_truncates_to_zero() -> None:
    result = compute_royalty_amount(offered_amount=-50, royalty_split=1, percentage=100)
    assert result == uint64(0)
```
