### Title
NFT Royalty Bypass via Integer Division Truncation to Zero in Offer Settlement - (File: chia/wallet/nft_wallet/nft_wallet.py)

### Summary
The `compute_royalty_amount` function and the `trade_prices_list` filter in `make_nft1_offer` both use integer floor division (`//`). When the offered fungible amount is small enough that the royalty calculation truncates to zero, the wallet omits the royalty payment entirely from the NFT spend's `trade_prices_list`, bypassing the CLVM-level royalty enforcement mechanism. An unprivileged secondary seller can exploit this to transfer an NFT without paying the creator's royalty.

### Finding Description

`compute_royalty_amount` in `chia/wallet/nft_wallet/nft_wallet.py` computes royalties using two sequential integer floor divisions:

```python
amount = abs(offered_amount) // royalty_split * percentage // MAX_ROYALTY_BASIS_POINTS
``` [1](#0-0) 

`MAX_ROYALTY_BASIS_POINTS` is 10000. For an NFT with a 1% royalty (100 basis points) and an offered amount of 99 mojos:

```
99 // 1 * 100 // 10000 = 9900 // 10000 = 0
```

The existing test `test_small_amount_truncates_to_zero` explicitly confirms this behavior is reachable: [2](#0-1) 

In `make_nft1_offer`, when the royalty rounds to zero, the `CreateCoin` for the royalty payment is created with `amount=0`: [3](#0-2) 

The announcement assertion loop then filters out zero-amount payments, so no royalty announcement is required in the spend bundle: [4](#0-3) 

Critically, the `trade_prices_list` passed to the NFT ownership layer puzzle spend is also filtered to exclude any price where the royalty would be zero: [5](#0-4) 

When this list is empty, the CLVM NFT ownership layer puzzle has no trade prices to enforce, so it does not require any royalty payment coin to be created. The NFT is transferred with a valid spend bundle that contains no royalty output.

Additionally, when the total royalty sum is zero, the royalty coin spend is skipped entirely: [6](#0-5) 

### Impact Explanation

A secondary NFT seller can bypass the creator's royalty by creating an offer for a sufficiently small on-chain amount (e.g., 99 mojos for a 1% royalty NFT). The buyer compensates the seller off-chain for the real value. The NFT creator receives zero royalty despite having set a non-zero royalty percentage at mint time. This constitutes unauthorized offer settlement affecting NFTs — the royalty enforcement that the NFT creator embedded in the NFT is silently nullified.

### Likelihood Explanation

Any unprivileged user holding an NFT with royalties can construct this offer through the standard wallet RPC (`create_offer_for_ids`). No special access, keys, or privileges are required. The threshold amount below which royalties round to zero is `MAX_ROYALTY_BASIS_POINTS / royalty_percentage - 1` mojos (e.g., for 1% royalty: 9999 mojos; for 0.01% royalty: 999,999 mojos). The attacker and buyer simply need to agree off-chain on the real compensation.

### Recommendation

Replace the floor division in `compute_royalty_amount` with ceiling division (round up) so that any non-zero royalty percentage on any non-zero trade amount always produces at least 1 mojo of royalty:

```python
import math
amount = math.ceil(abs(offered_amount) / royalty_split * percentage / MAX_ROYALTY_BASIS_POINTS)
```

Or using integer arithmetic:
```python
amount = (abs(offered_amount) * percentage + royalty_split * MAX_ROYALTY_BASIS_POINTS - 1) // (royalty_split * MAX_ROYALTY_BASIS_POINTS)
```

Additionally, the `trade_prices_list` filter at line 896 should not exclude prices that produce zero royalty — instead, the minimum enforced royalty should be 1 mojo when the percentage is non-zero.

### Proof of Concept

1. Alice mints an NFT with `royalty_percentage = 100` (1%).
2. Bob (secondary holder) calls `create_offer_for_ids` offering the NFT in exchange for 99 mojos of XCH.
3. Wallet computes: `compute_royalty_amount(-99, 1, 100)` → `99 * 100 // 10000` = `0`.
4. `royalty_payments[None]` = `[(launcher_id, CreateCoin(alice_ph, 0, [...]))]`.
5. Announcement loop skips the zero-amount payment (`if p.amount > 0`).
6. `trade_prices_list` filter: `99 * 100 // 10000 == 0` → list is empty.
7. NFT spend is constructed with empty `trade_prices_list`; CLVM puzzle enforces no royalty.
8. Carol accepts the offer, pays 99 mojos on-chain, compensates Bob off-chain.
9. Alice receives 0 royalty. The NFT ownership transfers successfully on-chain. [7](#0-6) [8](#0-7) [9](#0-8) [5](#0-4)

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
