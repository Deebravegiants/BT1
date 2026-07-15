### Title
NFT Royalty Bypass via Integer Division Truncation to Zero in Offer Settlement - (File: chia/wallet/nft_wallet/nft_wallet.py)

### Summary
`compute_royalty_amount` uses sequential integer floor-division that truncates to zero for small offered amounts. When the computed royalty is zero, `make_nft1_offer` explicitly skips the royalty coin creation and omits the corresponding `AssertPuzzleAnnouncement` from the spend bundle. An unprivileged buyer can craft offers with amounts small enough to produce a zero royalty, then repeat the pattern across multiple trades to transfer NFT value while paying no royalties to the creator.

### Finding Description
`compute_royalty_amount` in `chia/wallet/nft_wallet/nft_wallet.py` computes the royalty as:

```python
amount = abs(offered_amount) // royalty_split * percentage // MAX_ROYALTY_BASIS_POINTS
```

Two integer floor-divisions are applied in sequence. For any `offered_amount` where `abs(offered_amount) // royalty_split * percentage < 10000`, the result is zero. The project's own test suite explicitly documents and accepts this:

```python
def test_small_amount_truncates_to_zero() -> None:
    result = compute_royalty_amount(offered_amount=-50, royalty_split=1, percentage=100)
    assert result == uint64(0)
```

`make_nft1_offer` then propagates this zero through two critical paths:

1. **Announcement skipping** — royalty `AssertPuzzleAnnouncement` conditions are only added when `p.amount > 0`, so a zero-royalty payment generates no on-chain announcement requirement.

2. **Royalty coin skipping** — the entire royalty coin spend is skipped when the total payment sum is zero.

Additionally, the `trade_prices_list` passed to the NFT puzzle spend filters out entries where the computed royalty would be zero:

```python
trade_prices_list=[
    list(price)
    for price in trade_prices
    if price[0] * offered_royalty_percentages[asset] // MAX_ROYALTY_BASIS_POINTS != 0
],
```

This means the on-chain NFT transfer program CLVM puzzle receives an empty `trade_prices_list` and generates no royalty `CREATE_COIN` conditions, making the spend valid without any royalty payment.

### Impact Explanation
NFT creators who set a royalty percentage on their NFT1 tokens receive zero royalties when buyers structure offers with amounts below the truncation threshold. For a 1% royalty (100 basis points), any offered amount below 100 mojos produces zero royalty. A buyer can split a larger intended purchase into many small offers — each below the threshold — and transfer the full economic value of the NFT while paying no royalties. This is a direct bypass of offer settlement accounting affecting XCH and CAT assets.

### Likelihood Explanation
The threshold amounts are very small in absolute terms (sub-100 mojos for typical royalty percentages), making the bypass economically meaningful only for NFTs priced in the sub-mojo-hundred range or when royalty percentages are very low (e.g., 1 basis point). However, the bypass is unconditionally reachable by any unprivileged user who constructs an offer with a sufficiently small amount, requires no special access, and is confirmed by the existing test suite as accepted behavior.

### Recommendation
Round royalty calculations in the protocol's favor (ceiling division) rather than floor division:

```python
import math
amount = math.ceil(abs(offered_amount) / royalty_split * percentage / MAX_ROYALTY_BASIS_POINTS)
```

Or using integer arithmetic:
```python
amount = (abs(offered_amount) * percentage + royalty_split * MAX_ROYALTY_BASIS_POINTS - 1) // (royalty_split * MAX_ROYALTY_BASIS_POINTS)
```

This ensures that any non-zero royalty percentage on any non-zero trade amount always results in at least 1 mojo of royalty, preventing the bypass.

### Proof of Concept

**Truncation to zero (confirmed by existing test):**
- `offered_amount = -50`, `royalty_split = 1`, `percentage = 100` (1% royalty)
- `50 // 1 * 100 // 10000 = 5000 // 10000 = 0` → royalty = 0

**Bypass pattern for a 1% royalty NFT:**
- Buyer structures offer: `offered_amount = -99 mojos`
- `99 * 100 // 10000 = 9900 // 10000 = 0` → zero royalty
- `make_nft1_offer` skips royalty announcement (line 853: `if p.amount > 0`)
- `make_nft1_offer` skips royalty coin spend (line 911: `if sum(...) == 0: continue`)
- NFT spend bundle submitted with empty `trade_prices_list` (line 896)
- Offer settles on-chain; creator receives 0 mojos instead of expected 0.99 mojos

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** chia/wallet/nft_wallet/nft_wallet.py (L846-855)
```python
            announcements_to_assert.extend(
                [
                    AssertPuzzleAnnouncement(
                        asserted_ph=royalty_ph,
                        asserted_msg=Program.to((launcher_id, [p.as_condition_args()])).get_tree_hash(),
                    )
                    for launcher_id, p in payments
                    if p.amount > 0
                ]
            )
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
