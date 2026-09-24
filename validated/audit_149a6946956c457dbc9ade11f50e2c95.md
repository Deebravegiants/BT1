### Title
Unrestricted token-metadata cloning in `Bonding.launch` enables lookalike-token phishing of traders - ([File: packages/contracts/src/Bonding.sol])

### Summary
CVE-2026-3925 concerns Chrome's `LookalikeChecks` failing to stop a page from visually impersonating a trusted origin, deceiving the user into acting on the wrong (spoofed) entity. Alt.fun's `Bonding.launch` has the analogous gap: any unprivileged address can call `Zap.createToken` and mint a brand-new bonding curve whose `name`, `ticker`, `description`, `image`, and `urls` are byte-for-byte identical to an existing (or a well-known, trending) token's metadata. There is no on-chain uniqueness or provenance check binding this display metadata to a canonical token address, so a trader who visually identifies a token by its name/ticker/logo (exactly the class of check `LookalikeChecks` is supposed to enforce) can be lured into sending USDC into a cloned, attacker-controlled curve instead of the genuine one.

### Finding Description
`Bonding.launch` only bounds the *length* of the launch metadata fields, it never checks them for uniqueness or collision with any prior launch: [1](#0-0) 

`_storeTokenInfo` then persists whatever `name`/`ticker`/`description`/`image`/`urls` the caller supplied, verbatim, with no cross-token dedup: [2](#0-1) 

The salt-mixing design that determines the CREATE2 address explicitly folds in the caller's address, so two *different* creators can launch tokens with the identical `(name, ticker)` pair and simply land at two different addresses — this is a documented, tested property, not an edge case: [3](#0-2) 

Because `Zap.createToken`/`Bonding.launch` is fully permissionless (gated only by the `$20` `MIN_SEED_USDC` floor and the LT-existence check), an attacker can:
1. Observe a trending or about-to-launch token's `name`, `ticker`, `description`, `image` and social `urls`.
2. Call `Zap.createToken` with identical metadata but their own `ltAddress`/salt, producing a distinct contract address with a fully authentic-looking on-chain `TokenInfo` (same name/ticker/logo/socials as the real token).
3. Publicize or otherwise route traffic to the clone's contract address.

Traders and even automated aggregators that key off `name`/`ticker`/`image` (rather than double-checking the exact contract address, the analog of the browser address bar the CVE's `LookalikeChecks` are meant to protect) end up calling `Zap.buy` against the impostor curve.

### Impact Explanation
Funds sent to `Zap.buy` on the impostor curve are consumed exactly like any other legitimate buy: USDC is charged the 0.75% Alt Fun fee (with the creator share routed to the attacker via `FeeVault.accrue`/`claim`) and the rest is minted into LT and consumed by the clone's `Bonding` curve, crediting the attacker's own token supply: [4](#0-3) 

The trader receives tokens from the wrong, worthless curve while believing they bought the genuine project — a concrete, permanent theft of trader funds redirected to the attacker's wallet (as both curve proceeds and as `creatorBalance` fee accrual), with no on-chain mechanism to correct or reverse the misattribution.

### Likelihood Explanation
The attack is trivial and cheap: it requires only a single unprivileged `Zap.createToken` call funded with the $20 minimum seed, no special timing, no privileged role, and no interaction with any other protocol component. Because the only address-uniqueness constraint (`_checkVanity`/CREATE2 salt) is keyed off `(creator, name, ticker, salt)`, it does nothing to stop metadata cloning by a different creator — this is confirmed by the project's own test suite (`test_predictTokenAddress_differentCreators_differentAddresses`) treating same-name/ticker launches by different creators as an expected, successful case.

### Recommendation
Add an on-chain uniqueness/registry check in `Bonding.launch` (e.g., a mapping of `keccak256(name, ticker)` — or a normalized/case-folded variant — to the first token that claimed it) and reject subsequent launches that collide, or otherwise flag/label non-first claimants distinctly. Consider similarly restricting `image`/`urls` reuse, or exposing on-chain provenance (e.g., emitting a "first-claim" flag in `TokenLaunched`) so frontends and aggregators can reliably distinguish the canonical token from clones without relying purely on display metadata.

### Proof of Concept
1. Token A launches: `Zap.createToken({name: "PopularCoin", ticker: "POP", image: "ipfs://logo", urls: [...] , ltAddress: LT}, seedUsdc)` → deployed at address `T_A`.
2. Attacker (any unprivileged address) calls `Zap.createToken({name: "PopularCoin", ticker: "POP", image: "ipfs://logo", urls: [...] , ltAddress: LT}, MIN_SEED_USDC)` with their own mined salt → deployed at a different address `T_B`, with `Bonding.getTokenInfo(T_B)` returning metadata indistinguishable from `T_A`'s (see `_storeTokenInfo`, `Bonding.sol:537-554`).
3. Attacker advertises `T_B` as "PopularCoin" (e.g., via social media, a spoofed link, or a compromised listing) — victims call `Zap.buy(T_B, usdcAmount, ...)` believing they are buying `T_A`.
4. Victim USDC is fee-split and curve-consumed against `T_B`; the attacker (creator of `T_B`) accrues the creator-fee share in `FeeVault.creatorBalance[attacker]` and can `claim()` it, while the victim holds tokens on a worthless clone curve with no path to recover funds or migrate to `T_A`.

### Citations

**File:** packages/contracts/src/Bonding.sol (L402-410)
```text
        uint256 nameLen = bytes(params.name).length;
        if (nameLen < MIN_NAME_LENGTH || nameLen > MAX_NAME_LENGTH) revert InvalidNameLength();
        uint256 tickerLen = bytes(params.ticker).length;
        if (tickerLen < MIN_TICKER_LENGTH || tickerLen > MAX_TICKER_LENGTH) revert InvalidTickerLength();
        if (bytes(params.description).length > MAX_DESCRIPTION_LENGTH) revert InvalidDescriptionLength();
        if (bytes(params.image).length > MAX_IMAGE_LENGTH) revert InvalidImageLength();
        for (uint256 i = 0; i < 3; i++) {
            if (bytes(params.urls[i]).length > MAX_URL_LENGTH) revert InvalidUrlLength();
        }
```

**File:** packages/contracts/src/Bonding.sol (L537-554)
```text
    function _storeTokenInfo(
        address tokenAddr,
        address pair,
        LaunchParams calldata params,
        address creator_
    ) internal {
        _s().tokenInfo[tokenAddr] = TokenInfo({
            creator: creator_,
            pair: pair,
            ltAddress: params.ltAddress,
            name: params.name,
            ticker: params.ticker,
            description: params.description,
            image: params.image,
            urls: params.urls,
            lifecycle: Lifecycle.Curve
        });
    }
```

**File:** packages/contracts/test/Clones.t.sol (L62-89)
```text
    function test_predictTokenAddress_differentCreators_differentAddresses() public {
        // Property check (no launch): same userSalt yields different
        // predicted addresses for different creators. This is what
        // `_mixSalt(creator, name, ticker, userSalt)` guarantees, preventing
        // front-running of mined vanity salts. Uses an arbitrary salt —
        // `predictTokenAddress` is a view that doesn't enforce the vanity
        // suffix.
        bytes32 sharedSalt = keccak256("collision-check");
        address predA = bonding.predictTokenAddress(creator, NAME, TICKER, sharedSalt);
        address predB = bonding.predictTokenAddress(trader, NAME, TICKER, sharedSalt);
        assertTrue(predA != predB, "different creators must yield different addresses");

        // Sanity: each creator can launch successfully with their own
        // independently-mined vanity salt and lands at the predicted address.
        bytes32 saltA = _mineForParams(creator);
        bytes32 saltB = _mineForParams(trader);
        address expA = bonding.predictTokenAddress(creator, NAME, TICKER, saltA);
        address expB = bonding.predictTokenAddress(trader, NAME, TICKER, saltB);

        vm.prank(creator);
        (address tokenA,) = bonding.launch(_params(saltA), creator);
        vm.prank(trader);
        (address tokenB,) = bonding.launch(_params(saltB), trader);

        assertEq(tokenA, expA);
        assertEq(tokenB, expB);
        assertTrue(tokenA != tokenB);
    }
```

**File:** packages/contracts/src/FeeVault.sol (L101-123)
```text
    function accrue(
        address token,
        address creator,
        uint256 creatorAmount,
        uint256 protocolAmount,
        bool isBuy
    ) external onlyDepositor {
        FeeVaultStorage storage $ = _s();
        if (creatorAmount > 0) {
            if (creator == address(0)) revert ZeroAddress();
            $.creatorBalance[creator] += creatorAmount;
            $.totalAccruedCreator += creatorAmount;
            $.lifetimeCreatorEarned[creator] += creatorAmount;
        }
        if (protocolAmount > 0) {
            $.protocolBalance += protocolAmount;
            $.lifetimeProtocolEarned += protocolAmount;
        }
        if ($.usdc.balanceOf(address(this)) < $.totalAccruedCreator + $.protocolBalance) {
            revert UnderfundedAccrual();
        }
        emit FeeAccrued(token, creator, creatorAmount, protocolAmount, isBuy);
    }
```
