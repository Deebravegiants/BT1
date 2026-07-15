### Title
NFT Royalty Bypass via Integer Division Truncation to Zero in `compute_royalty_amount` - (File: `chia/wallet/nft_wallet/nft_wallet.py`)

### Summary
`compute_royalty_amount` uses integer floor division that can produce 0 for small fungible amounts. When this happens, the wallet silently omits the royalty payment and passes an empty `trade_prices_list` to the NFT ownership-layer puzzle, causing the on-chain royalty transfer program to enforce no royalty. An NFT seller can exploit this to transfer a royalty-bearing NFT without paying the creator their entitled royalty.

### Finding Description

`compute_royalty_amount` in `chia/wallet/nft_wallet/nft_wallet.py` computes royalties using sequential integer floor division:

```python
amount = abs(offered_amount) // royalty_split * percentage // MAX_ROYALTY_BASIS_POINTS
``` [1](#0-0) 

`MAX_ROYALTY_BASIS_POINTS` is 10000. For small `offered_amount` values, the intermediate product `abs(offered_amount) // royalty_split * percentage` can be less than 10000, causing the final division to truncate to 0. The existing test `test_small_amount_truncates_to_zero` explicitly confirms this: `compute_royalty_amount(offered_amount=-50, royalty_split=1, percentage=100)` returns `uint64(0)`. [2](#0-1) 

When `compute_royalty_amount` returns 0, two downstream effects in `make_nft1_offer` silently bypass royalty enforcement:

**Effect 1 — Announcement guard skips zero-amount payments:**

```python
for launcher_id, p in payments
    if p.amount > 0   # zero-royalty payments are excluded from announcements
``` [3](#0-2) 

**Effect 2 — `trade_prices_list` passed to the NFT puzzle is filtered to empty:**

```python
trade_prices_list=[
    list(price)
    for price in trade_prices
    if price[0] * offered_royalty_percentages[asset] // MAX_ROYALTY_BASIS_POINTS != 0
],
``` [4](#0-3) 

When `trade_prices_list` is empty, the NFT ownership-layer puzzle's royalty transfer program has no trade prices to compute royalties from, so it enforces zero royalty on-chain. The royalty coin spend is also skipped entirely:

```python
if sum(p.amount for _, p in payments) == 0:
    continue
``` [5](#0-4) 

### Impact Explanation

An NFT seller (unprivileged) can create an offer requesting a sufficiently small fungible amount (e.g., 50 mojos XCH for an NFT with a 1% royalty: `50 * 100 // 10000 = 0`) to cause the royalty to truncate to zero. The resulting offer spend bundle passes an empty `trade_prices_list` to the NFT puzzle, so the on-chain royalty transfer program enforces no royalty payment. The NFT creator is deprived of their entitled royalty in the offer settlement. This is an accounting change affecting NFT offer settlement.

### Likelihood Explanation

Any NFT seller who requests a small enough fungible amount triggers this path. The threshold is `offered_amount < MAX_ROYALTY_BASIS_POINTS / royalty_percentage` mojos (e.g., for a 1% royalty NFT, any offer requesting fewer than 10,000 mojos triggers zero royalty). This is reachable by any unprivileged user creating a valid offer.

### Recommendation

Add a zero-royalty guard in `compute_royalty_amount` or at the call site in `make_nft1_offer`. If the computed royalty is 0 but the percentage is non-zero and the offered amount is non-zero, either raise an error or round up to 1 mojo (ceiling division). The `trade_prices_list` filter at line 896 should similarly use ceiling arithmetic rather than silently dropping the trade price.

```python
# In compute_royalty_amount, use ceiling division:
amount = (abs(offered_amount) // royalty_split * percentage + MAX_ROYALTY_BASIS_POINTS - 1) // MAX_ROYALTY_BASIS_POINTS
```

Or reject offers where the royalty would truncate to zero:

```python
if amount == 0 and percentage > 0:
    raise ValueError("Offered amount too small to compute non-zero royalty")
```

### Proof of Concept

```python
from chia.wallet.nft_wallet.nft_wallet import compute_royalty_amount
from chia_rs.sized_ints import uint64

# NFT with 1% royalty (100 basis points), offered for 50 mojos
result = compute_royalty_amount(offered_amount=-50, royalty_split=1, percentage=100)
assert result == uint64(0)  # royalty silently truncated to zero

# Consequence: trade_prices_list filter at line 896:
# price[0] * royalty_percentage // MAX_ROYALTY_BASIS_POINTS
# = 50 * 100 // 10000 = 0  → trade price excluded → empty list passed to NFT puzzle
# → royalty transfer program enforces 0 royalty on-chain
``` [6](#0-5) [7](#0-6)

### Citations

**File:** chia/wallet/nft_wallet/nft_wallet.py (L57-68)
```python
MAX_ROYALTY_BASIS_POINTS = 10000


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

**File:** chia/wallet/nft_wallet/nft_wallet.py (L793-800)
```python
        royalty_payments: dict[bytes32 | None, list[tuple[bytes32, CreateCoin]]] = {}
        for asset, amount in fungible_asset_dict.items():  # offered fungible items
            if amount < 0 and request_side_royalty_split > 0:
                payment_list: list[tuple[bytes32, CreateCoin]] = []
                for launcher_id, address, percentage in required_royalty_info:
                    extra_royalty_amount = compute_royalty_amount(amount, request_side_royalty_split, percentage)
                    payment_list.append((launcher_id, CreateCoin(address, extra_royalty_amount, [address])))
                royalty_payments[asset] = payment_list
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

**File:** chia/wallet/nft_wallet/nft_wallet.py (L910-912)
```python
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
