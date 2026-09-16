Found the strongest analog. `HyperFungibleToken`'s relayer allowlist is **opt-in**: `_checkRelayer` only rejects a delivery when a relayer has actually been set, meaning any token deployer who forgets to call `setRelayer` leaves `onAccept`/`onPostRequestTimeout` open to mint against a delivery from *any* relayer, with only documentation (not an enforced block) warning against it. This is structurally identical to the Trail-of-Bits finding: a security-critical default is left to the deployer/user to actively opt into, and skipping it silently degrades the app from a trusted-relayer-gated mint to a fully open one — reachable by any relayer's forged/unintended delivery, with real fund-mint consequences. [1](#0-0) [2](#0-1) 

### Title
Base `HyperFungibleToken._checkRelayer` fails open by default, allowing unrestricted mint until the deployer opts in to `setRelayer` — ([File: evm/src/apps/HyperFungibleToken.sol])

### Summary
`HyperFungibleToken`, the library contract from which apps like `BridgeToken` are built, implements a relayer allowlist as an **opt-in** gate: `_checkRelayer` only rejects an incoming delivery when a relayer has been explicitly configured via `setRelayer`. If a deployer never calls `setRelayer` (the default state of any freshly deployed token from this package), `onAccept` and `onPostRequestTimeout` accept a delivery from **any** relayer and mint tokens to the address specified in the incoming request body. This mirrors the reported iCloud-backup pattern precisely: a security control that should be mandatory is instead offered as an optional step, and omitting it (the "unencrypted"/"no relayer set" state) is the silent default rather than a blocked state.

### Finding Description
`HyperFungibleToken.onAccept`/`onPostRequestTimeout` are `public virtual`, gated only by `onlyHost` and `whenNotPaused`, then check source chain membership and mint based on the request body [1](#0-0) . The base contract's `_checkRelayer` "only rejects when a relayer has been set" [3](#0-2) , meaning a zero/unset `_relayer` is treated as "allowlist disabled" rather than "fail closed." This design decision was explicitly acknowledged as risky: "Failing closed there would leave every token deployed without a `setRelayer` call unable to receive anything, with no compile-time signal" [4](#0-3) . `BridgeToken` — Hyperbridge's own BRIDGE token — had to explicitly override `_checkRelayer` to fail closed instead of inheriting the safe default [5](#0-4) , confirming that the base library's behavior is the insecure one and every other consumer of `HyperFungibleToken` inherits it unless they remember to add the same override or call `setRelayer` before going live.

The commit history confirms an earlier iteration treated an unset relayer identically ("Zero relayer fails closed") before this exact tradeoff was reconsidered and *reversed* to the current opt-in model [6](#0-5) , showing this is a conscious, documented tradeoff of security for deployer convenience — the exact "footgun with a warning" pattern described in the report.

### Impact Explanation
Any `HyperFungibleToken`-based app deployed without calling `setRelayer` (the state of a freshly deployed proxy/contract, and the default state that persists until a deployer takes an extra step) accepts `onAccept`/`onPostRequestTimeout` deliveries from **any relayer**, not just a designated one. Since these callbacks mint tokens based on the message body's `to`/`amount` fields, an attacker who can get any valid state/consensus proof delivered through the host (which is by design permissionless — "Permissionless (can be called by anyone)" [7](#0-6) ) can mint unbacked tokens or trigger unauthorized refunds, since the mint logic trusts the message body without any additional relayer-specific authorization. This is unbacked mint / unauthorized app action — direct fund-safety impact for every token deployed from this library that has not explicitly hardened the default.

### Likelihood Explanation
High, because the vulnerable state is the *default*: any developer using the published `HyperFungibleToken` library (a first-class, documented Hyperbridge app pattern) who does not proactively call `setRelayer`, or forgets to override `_checkRelayer` the way `BridgeToken` does, ships an open mint. Given the general permissionless nature of message delivery to `IApp` callbacks on Hyperbridge, this requires no special privilege — only a standard-path message delivery to an unconfigured deployment.

### Recommendation
- Short term: Change `HyperFungibleToken._checkRelayer`'s default to fail closed (reject when `_relayer == address(0)`), matching `BridgeToken`'s override, and require `setRelayer` to be called as part of `configure`/initialization rather than as an optional post-deployment step.
- Long term: Remove the ability to reach a "relayer unset" live state entirely — e.g., require the relayer address as a constructor/initializer parameter so a token can never be deployed and made operational (`configure`d, unpaused) without one, eliminating the silent insecure default altogether.

### Proof of Concept
The project's own test suite documents the exploitable gap: `testFreshTokenRejectsEveryRelayerUntilSet` in `BridgeTokenTest.t.sol` demonstrates that only the hardened `BridgeToken` override rejects an unset-relayer state, while the base `HyperFungibleToken` contract on which it is built defaults to accepting any relayer until `setRelayer` is called [8](#0-7) . Any other project deploying the unmodified base library and skipping `setRelayer` (or forgetting to override `_checkRelayer`) is left in the exploitable "any relayer mints" state by default, with no compile-time or deployment-time enforcement preventing it.

### Citations

**File:** sdk/packages/core/docs/ai/flows/the-bridge-token-s-relayer-gate-and-why-the-base-token-has-none.md (L10-12)
```markdown
3. `HyperFungibleToken.onAccept` and `onPostRequestTimeout` are `public virtual`, run `onlyHost`
   and `whenNotPaused`, then check the source against `_supportedChains`, decode the body, and
   mint. The base token knows nothing about relayers: a third-party token accepts every relayer.
```

**File:** sdk/packages/core/docs/ai/decisions/2026-09-03-hyperfungibletoken-opts-in-to-the-relayer-gate-bridgetoken.md (L3-11)
```markdown
Chosen: the base token's `_checkRelayer` only rejects when a relayer has been set, and
`BridgeToken` overrides it so that an unset relayer matches nobody.

`HyperFungibleToken` is a library contract that third parties deploy from this package. Failing
closed there would leave every token deployed without a `setRelayer` call unable to receive
anything, with no compile-time signal. The BRIDGE token is ours, its supply is backed by the nexus
escrow, and a forged mint is exactly the attack the gate exists for, so it takes the strict
semantics of the intent gateway. The two behaviours live in one virtual function so the difference
is visible in one place rather than spread through the callbacks.
```

**File:** evm/src/apps/BridgeToken.sol (L100-107)
```text
    /**
     * @dev Fails closed: with no relayer set nobody may deliver. The supply of this token is backed
     * by the nexus escrow, so it must not mint on the strength of a consensus proof alone. The
     * handler always forwards a real `msg.sender`, so zero never matches.
     */
    function _checkRelayer(address incomingRelayer) private view {
        if (incomingRelayer != _relayer) revert UnauthorizedRelayer();
    }
```

**File:** sdk/packages/core/docs/ai/decisions/2026-09-03-zero-relayer-fails-closed-and-the-upgrade-arms-it-atomically.md (L1-11)
```markdown
# 2026-09-03 — Zero relayer fails closed, and the upgrade arms it atomically

Superseded on 2026-09-05: an unset relayer gates nothing, see above.

Chosen: an unset `_relayer` matches no delivery, because the handler always forwards a real
`msg.sender`. The rollout sets it in the upgrade transaction via `upgradeToAndCall` calldata.

Alternative rejected — treat zero as "allowlist disabled". Convenient for tests and a forgotten
init, but it makes the safe state opt-in, and a fresh proxy would run unguarded until someone
noticed. A refused delivery costs nothing: the host deletes the receipt and the authorised relayer
can resubmit.
```

**File:** docs/content/developers/evm/api/ihandler.mdx (L85-101)
```text
### handlePostRequests()

Processes and delivers POST requests to destination applications.

```solidity lineNumbers
function handlePostRequests(
    IHost host,
    PostRequestMessage calldata request
) external
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `host` | `IHost` | The IHost contract |
| `request` | `PostRequestMessage` | Struct containing proof and requests |

**Access:** Permissionless (can be called by anyone)
```

**File:** evm/tests/foundry/BridgeTokenTest.t.sol (L173-196)
```text
    /// Unlike the base token, no relayer means nobody may deliver, so a deployment that skipped
    /// `setRelayer` cannot mint.
    function testFreshTokenRejectsEveryRelayerUntilSet() public {
        BridgeToken fresh = new BridgeToken(address(this));
        fresh.configure(
            HyperFungibleToken.ConfigOptions({host: address(host), dispatcher: address(callDispatcher)})
        );
        assertEq(fresh.relayer(), address(0));
        PostRequest memory request = _fromNexus(palletId, RECIPIENT, MINT_AMOUNT);
        request.to = abi.encodePacked(address(fresh));

        vm.prank(address(host));
        vm.expectRevert(BridgeToken.UnauthorizedRelayer.selector);
        fresh.onAccept(IncomingPostRequest({request: request, relayer: relayer}));
        vm.prank(address(host));
        vm.expectRevert(BridgeToken.UnauthorizedRelayer.selector);
        fresh.onAccept(IncomingPostRequest({request: request, relayer: address(0xD00D)}));
        assertEq(fresh.totalSupply(), 0);

        fresh.setRelayer(relayer);
        vm.prank(address(host));
        fresh.onAccept(IncomingPostRequest({request: request, relayer: relayer}));
        assertEq(fresh.balanceOf(RECIPIENT), MINT_AMOUNT);
    }
```
