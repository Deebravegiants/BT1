Confirmed: `Zap.createToken` passes `msg.sender` directly as `creator_` to `Bonding.launch` [1](#0-0) , and `transferCreator` lets the current creator reassign this role to any address without validation [2](#0-1) . There is no `claimFor`/delegate claim path in `FeeVault` — only `claim()` gated to `msg.sender` and the permissionless `claimProtocol()`.

### Title
Creator fee funds permanently freeze in `FeeVault` if `creator` is set to a contract unable to call `claim()` - ([File: packages/contracts/src/FeeVault.sol])

### Summary
`FeeVault.claim()` pays out only to `msg.sender`'s own pooled `creatorBalance`, with no way for any other address to trigger a payout on the creator's behalf. Both `Bonding.launch` (which sets the initial creator to any caller-supplied address) and `Bonding.transferCreator` (which lets the current creator reassign the role to any address at all) allow the `creator` role to be attached to an address that is an immutable smart contract, a multisig without the exact call wired up, or any other contract that cannot itself invoke `FeeVault.claim()`. Once fees accrue to that `creatorBalance[creator]` slot, they are permanently unclaimable, since `FeeVault` has no admin rescue and no `claimFor`/delegated-claim mechanism — this is the exact bug class from the analog report, applied to alt.fun's fee-accrual design.

### Finding Description
`FeeVault.accrue` credits `creatorBalance[creator]` using the creator address recorded in `Bonding.tokenInfo(token).creator` [3](#0-2) . That creator address originates from the `creator_` parameter passed into `Bonding.launch`, which is forwarded verbatim from `Zap.createToken`'s `msg.sender` with no restriction on it being an EOA [1](#0-0) [4](#0-3) . The role can also be reassigned later via `transferCreator`, which only checks `newCreator != address(0)` and `newCreator != info.creator` — it never checks that `newCreator` can actually receive/claim funds [2](#0-1) .

`FeeVault.claim()` is hard-restricted to `msg.sender`:
```solidity
function claim() external nonReentrant returns (uint256 amount) {
    amount = $.creatorBalance[msg.sender];
    ...
    $.usdc.safeTransfer(msg.sender, amount);
}
``` [5](#0-4) 

If `creator` is a contract deployed without a function that calls `FeeVault.claim()` (e.g., a vanity CREATE2 contract launched by a smart-contract wallet lacking arbitrary-call capability, an immutable vault, or a contract that self-destructed/became unusable), every dollar of the 0.25% creator fee share accrued to that address is permanently stuck. Unlike `claimProtocol()`, which the protocol deliberately made "permissionless — funds still go to the admin-set address" precisely to avoid a single point of claim failure [6](#0-5) , no equivalent safety valve exists for creator balances. There is also no owner-only rescue/sweep path for `creatorBalance` (only `sweepDonations()`, which explicitly excludes backed/accrued balances) [7](#0-6) .

### Impact Explanation
Fees continuously accrue to the frozen `creatorBalance[creator]` slot on every buy/sell of the affected token (0.25% of the 0.75% total fee, per trade, forever, since the token keeps trading post-launch and post-graduation). These funds become permanently inaccessible, with no admin override, matching the "permanent freezing of creator funds" impact bar. Severity scales with trading volume of the token in question.

### Likelihood Explanation
The trigger requires either (a) launching a token where the creator is deliberately or accidentally set to an unclaimable contract address, or (b) an existing creator calling `transferCreator` to move the role to such an address (e.g. handing creatorship to a DAO/vault contract that turns out not to expose a `claim()`-calling function). Both paths are fully permissionless and reachable by any unprivileged account acting on their own token; no protocol privilege is required.

### Recommendation
Add a permissionless "claim for" variant, mirroring the design already used for `claimProtocol()`:
```solidity
function claimFor(address creator) external nonReentrant returns (uint256 amount) {
    amount = $.creatorBalance[creator];
    if (amount == 0) revert NothingToClaim();
    $.creatorBalance[creator] = 0;
    $.totalAccruedCreator -= amount;
    $.usdc.safeTransfer(creator, amount);
    emit CreatorFeesClaimed(creator, amount);
}
```
This allows any account to trigger the payout to the creator address, exactly as recommended in the analog report, while funds still always land at the intended `creator` address.

### Proof of Concept
1. Deploy (or reuse) an immutable contract `C` with no function that calls out to `FeeVault.claim()` (e.g. a minimal proxy with only a `receive()`).
2. Call `Zap.createToken(params, seedUsdc)` from `C` (or from an EOA, then call `Bonding.transferCreator(tokenAddr, address(C))`), making `C` the token's `creator`.
3. Trade the token via `Zap.buy` / `Zap.sell` — each trade calls `FeeVault.accrue(token, C, creatorAmount, protocolAmount, isBuy)`, incrementing `creatorBalance[C]`.
4. Attempt `FeeVault.claim()` from any address: it only ever reads/pays `creatorBalance[msg.sender]`; since `C` cannot originate a transaction to call `claim()` itself, `creatorBalance[C]` is permanently stuck with no other function in `FeeVault` able to release it to `C` or anyone else.

### Citations

**File:** packages/contracts/src/Zap.sol (L228-228)
```text
        (tokenAddr,) = _s().bonding.launch(params, msg.sender);
```

**File:** packages/contracts/src/Bonding.sol (L390-416)
```text
    function launch(
        LaunchParams calldata params,
        address creator_
    ) external onlyRouter nonReentrant returns (address tokenAddr, address pair) {
        if (params.ltAddress == address(0)) revert InvalidInput();
        BondingStorage storage $ = _s();
        // `Zap.createToken` is permissionless; without this gate a fake LT
        // could siphon USDC inside `mint` (which `Zap` `forceApprove`s).
        if (!IBounceFactory($.bounceGlobalStorage.factory()).ltExists(params.ltAddress)) {
            revert UnknownLeveragedToken(params.ltAddress);
        }

        uint256 nameLen = bytes(params.name).length;
        if (nameLen < MIN_NAME_LENGTH || nameLen > MAX_NAME_LENGTH) revert InvalidNameLength();
        uint256 tickerLen = bytes(params.ticker).length;
        if (tickerLen < MIN_TICKER_LENGTH || tickerLen > MAX_TICKER_LENGTH) revert InvalidTickerLength();
        if (bytes(params.description).length > MAX_DESCRIPTION_LENGTH) revert InvalidDescriptionLength();
        if (bytes(params.image).length > MAX_IMAGE_LENGTH) revert InvalidImageLength();
        for (uint256 i = 0; i < 3; i++) {
            if (bytes(params.urls[i]).length > MAX_URL_LENGTH) revert InvalidUrlLength();
        }

        bytes32 saltMixed = _mixSalt(creator_, params.name, params.ticker, params.salt);
        tokenAddr = Clones.predictDeterministicAddress($.tokenImplementation, saltMixed, address(this));
        _checkVanity(tokenAddr);

        _storeTokenInfo(tokenAddr, address(0), params, creator_);
```

**File:** packages/contracts/src/Bonding.sol (L738-748)
```text
    function transferCreator(
        address tokenAddress,
        address newCreator
    ) external {
        if (newCreator == address(0)) revert ZeroAddress();
        TokenInfo storage info = _s().tokenInfo[tokenAddress];
        if (msg.sender != info.creator) revert NotCreator();
        if (newCreator == info.creator) revert InvalidInput();
        info.creator = newCreator;
        emit CreatorTransferred(tokenAddress, msg.sender, newCreator);
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

**File:** packages/contracts/src/FeeVault.sol (L127-135)
```text
    function claim() external nonReentrant returns (uint256 amount) {
        FeeVaultStorage storage $ = _s();
        amount = $.creatorBalance[msg.sender];
        if (amount == 0) revert NothingToClaim();
        $.creatorBalance[msg.sender] = 0;
        $.totalAccruedCreator -= amount;
        $.usdc.safeTransfer(msg.sender, amount);
        emit CreatorFeesClaimed(msg.sender, amount);
    }
```

**File:** packages/contracts/src/FeeVault.sol (L137-145)
```text
    function claimProtocol() external nonReentrant returns (uint256 amount) {
        FeeVaultStorage storage $ = _s();
        amount = $.protocolBalance;
        if (amount == 0) revert NothingToClaim();
        $.protocolBalance = 0;
        address feeTo_ = $.feeTo;
        $.usdc.safeTransfer(feeTo_, amount);
        emit ProtocolFeesClaimed(feeTo_, amount);
    }
```

**File:** packages/contracts/src/FeeVault.sol (L151-160)
```text
    function sweepDonations() external nonReentrant returns (uint256 amount) {
        FeeVaultStorage storage $ = _s();
        uint256 backed = $.totalAccruedCreator + $.protocolBalance;
        uint256 balance = $.usdc.balanceOf(address(this));
        if (balance <= backed) revert NothingToClaim();
        amount = balance - backed;
        address feeTo_ = $.feeTo;
        $.usdc.safeTransfer(feeTo_, amount);
        emit DonationsSwept(feeTo_, amount);
    }
```
