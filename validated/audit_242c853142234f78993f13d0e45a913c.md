### Title
Bulk NFT Minting Accepts Unbounded Royalty Percentage, Permanently Corrupting Offer Settlement for Affected NFTs — (`chia/wallet/nft_wallet/nft_wallet.py`)

---

### Summary

The `nft_mint_bulk` RPC handler and the underlying `mint_from_did` / `mint_from_xch` bulk-minting functions accept a `royalty_pc` value of any `uint16` (0–65535) without validating it against the protocol maximum of 10 000 basis points (100%). Any value above 10 000 is silently curried into the NFT singleton puzzle at mint time. Because the royalty percentage is immutable once the singleton is launched, every subsequent attempt to settle an offer involving such an NFT raises an unhandled `ValueError` in `compute_royalty_amount`, permanently breaking offer settlement for the affected coin.

---

### Finding Description

**Validation present in the single-NFT path (not the bulk path):**

`generate_new_nft` explicitly rejects percentages above `MAX_ROYALTY_BASIS_POINTS`:

```python
if percentage > MAX_ROYALTY_BASIS_POINTS:
    raise ValueError(f"Royalty percentage {percentage} exceeds 100% ...")
``` [1](#0-0) 

The single-NFT RPC handler `nft_mint_nft` also has a partial guard (only for exactly 10 000):

```python
if request.royalty_percentage == 10000:
    raise ValueError("Royalty percentage cannot be 100%")
``` [2](#0-1) 

**No validation in the bulk path:**

`nft_mint_bulk` passes `request.royalty_percentage` (a raw `uint16`, range 0–65535) directly into the metadata dict without any bounds check:

```python
metadata_dict = {
    "program": metadata_program,
    "royalty_pc": request.royalty_percentage,   # ← no validation
    "royalty_ph": royalty_puzhash,
}
``` [3](#0-2) 

`mint_from_did` and `mint_from_xch` then forward `metadata["royalty_pc"]` directly to `create_ownership_layer_puzzle`, which curries it into the NFT transfer program without any check:

```python
inner_puzzle = create_ownership_layer_puzzle(
    launcher_coin.name(),
    b"",
    p2_inner_puzzle,
    metadata["royalty_pc"],          # ← unchecked
    royalty_puzzle_hash=metadata["royalty_ph"],
)
``` [4](#0-3) 

The identical unchecked path exists in `mint_from_xch`: [5](#0-4) 

**Consequence at offer settlement time:**

`compute_royalty_amount` raises `ValueError` for any percentage above `MAX_ROYALTY_BASIS_POINTS`:

```python
if percentage > MAX_ROYALTY_BASIS_POINTS:
    raise ValueError(f"NFT royalty percentage {percentage} exceeds 100% ...")
``` [6](#0-5) 

Because the royalty percentage is baked into the singleton puzzle at launch, it cannot be changed after minting. Every call to `make_nft1_offer` or `respond_to_offer` that involves such an NFT will raise this exception, permanently preventing offer-based trading. [7](#0-6) 

---

### Impact Explanation

An NFT minted via `nft_mint_bulk` with `royalty_percentage` between 10 001 and 65 535 is successfully committed to the blockchain (the CLVM puzzle does not validate the percentage). The royalty value is immutable. Any future holder of the NFT is permanently unable to sell it through the Chia offer system, because every offer-settlement code path calls `compute_royalty_amount` and receives an unhandled exception. This constitutes **corruption of offer/trade settlement state with direct security impact**: the NFT's market liquidity is permanently destroyed, and any buyer who receives such an NFT (e.g., via airdrop from a bulk mint) is trapped holding an untradeable asset.

---

### Likelihood Explanation

The attack requires no special privileges. Any wallet user with sufficient XCH to pay minting fees can call the `nft_mint_bulk` RPC endpoint and supply `royalty_percentage=uint16(10001)` (or any value up to 65 535). The NFT is minted and confirmed on-chain without error. The defect is only observable when a victim later attempts to trade the NFT via an offer.

---

### Recommendation

Add a bounds check in `nft_mint_bulk` before constructing the metadata list, mirroring the guard already present in `generate_new_nft`:

```python
if request.royalty_percentage is not None and request.royalty_percentage > MAX_ROYALTY_BASIS_POINTS:
    raise ValueError(
        f"Royalty percentage {request.royalty_percentage} exceeds 100% "
        f"({MAX_ROYALTY_BASIS_POINTS} basis points)"
    )
```

Additionally, add the same guard at the top of `mint_from_did` and `mint_from_xch` to protect callers that bypass the RPC layer:

```python
for meta in metadata_list:
    if meta["royalty_pc"] > MAX_ROYALTY_BASIS_POINTS:
        raise ValueError("royalty_pc exceeds 100%")
```

---

### Proof of Concept

1. Call `nft_mint_bulk` with `royalty_percentage=uint16(10001)`, a valid `uint16` value above the 100% cap.
2. `nft_mint_bulk` sets `"royalty_pc": uint16(10001)` in the metadata dict with no rejection. [8](#0-7) 
3. `mint_from_did` or `mint_from_xch` curries `10001` into the NFT transfer program puzzle. [4](#0-3) 
4. The NFT singleton is launched and confirmed on-chain with royalty = 10 001 bps.
5. Any subsequent call to `make_nft1_offer` or `respond_to_offer` for this NFT reaches `compute_royalty_amount(amount, split, 10001)`, which raises `ValueError("NFT royalty percentage 10001 exceeds 100%")`, aborting offer settlement. [6](#0-5) 
6. The NFT is permanently untradeable via the offer system. The existing test suite confirms that `generate_new_nft` rejects this value, but no equivalent test covers the `nft_mint_bulk` path. [9](#0-8)

### Citations

**File:** chia/wallet/nft_wallet/nft_wallet.py (L62-63)
```python
    if percentage > MAX_ROYALTY_BASIS_POINTS:
        raise ValueError(f"NFT royalty percentage {percentage} exceeds 100% ({MAX_ROYALTY_BASIS_POINTS} basis points)")
```

**File:** chia/wallet/nft_wallet/nft_wallet.py (L349-355)
```python
        # ensure percentage is uint16 and at most 100%
        try:
            percentage = uint16(percentage)
        except ValueError:
            raise ValueError(f"Percentage must be between 0 and {MAX_ROYALTY_BASIS_POINTS} (100%)")
        if percentage > MAX_ROYALTY_BASIS_POINTS:
            raise ValueError(f"Royalty percentage {percentage} exceeds 100% ({MAX_ROYALTY_BASIS_POINTS} basis points)")
```

**File:** chia/wallet/nft_wallet/nft_wallet.py (L797-799)
```python
                for launcher_id, address, percentage in required_royalty_info:
                    extra_royalty_amount = compute_royalty_amount(amount, request_side_royalty_split, percentage)
                    payment_list.append((launcher_id, CreateCoin(address, extra_royalty_amount, [address])))
```

**File:** chia/wallet/nft_wallet/nft_wallet.py (L1250-1256)
```python
            inner_puzzle = create_ownership_layer_puzzle(
                launcher_coin.name(),
                b"",
                p2_inner_puzzle,
                metadata["royalty_pc"],
                royalty_puzzle_hash=metadata["royalty_ph"],
            )
```

**File:** chia/wallet/nft_wallet/nft_wallet.py (L1491-1497)
```python
            inner_puzzle = create_ownership_layer_puzzle(
                launcher_coin.name(),
                b"",
                p2_inner_puzzle,
                metadata["royalty_pc"],
                royalty_puzzle_hash=metadata["royalty_ph"],
            )
```

**File:** chia/wallet/wallet_rpc_api.py (L2549-2550)
```python
        if request.royalty_percentage == 10000:
            raise ValueError("Royalty percentage cannot be 100%")
```

**File:** chia/wallet/wallet_rpc_api.py (L2976-2981)
```python
            metadata_dict = {
                "program": metadata_program,
                "royalty_pc": request.royalty_percentage,
                "royalty_ph": royalty_puzhash,
            }
            metadata_list.append(metadata_dict)
```
