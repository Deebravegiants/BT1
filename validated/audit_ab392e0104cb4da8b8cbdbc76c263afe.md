The entire module is deprecated — every public function, including `cancel_token_listing`, unconditionally aborts with `EDEPRECATED_MODULE` before touching any state. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** aptos-move/framework/aptos-token/sources/token_coin_swap.move (L1-1)
```text
/// Deprecated module
```

**File:** aptos-move/framework/aptos-token/sources/token_coin_swap.move (L44-50)
```text
    /// The listing of all tokens for swapping stored at token owner's account
    struct TokenListings<phantom CoinType> has key {
        // key is the token id for swapping and value is the min price of target coin type.
        listings: Table<TokenId, TokenCoinSwap<CoinType>>,
        listing_events: EventHandle<TokenListingEvent>,
        swap_events: EventHandle<TokenSwapEvent>,
    }
```

**File:** aptos-move/framework/aptos-token/sources/token_coin_swap.move (L154-161)
```text
    /// Cancel token listing for a fixed amount
    public fun cancel_token_listing<CoinType>(
        _token_owner: &signer,
        _token_id: TokenId,
        _token_amount: u64,
    ) {
        abort error::invalid_argument(EDEPRECATED_MODULE)
    }
```
