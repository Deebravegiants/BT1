## Analog Found: Missing relayer authorization gate on `BandwidthManager.onAccept`

### Title
Missing relayer-authorization check on `BandwidthManager.onAccept` allows treasury drain and price manipulation via forged/spoofed governance delivery - (File: `evm/src/apps/BandwidthManager.sol`)

### Summary
Every other governance-facing `IApp.onAccept` handler in this codebase (`HostManager`, `ExtrinsicIntents`/`IntentGatewayV2`, `BridgeToken`, `SimplexPaymaster`) was deliberately hardened with a `_checkRelayer`/`restrict(incoming.relayer, ...)` gate that restricts which relayer address may deliver privileged governance actions, on top of the `onlyHost` and `source == hyperbridge` checks. `BandwidthManager.onAccept` was never given this hardening: it enforces only `onlyHost` and `request.source.equals(hyperbridge)`, with no check on `incoming.relayer` at all, even though it dispatches `Withdraw` (arbitrary-beneficiary fund transfer) and `SetTiers` (arbitrary pricing) actions.

### Finding Description
`BandwidthManager.onAccept` is defined at [1](#0-0) :
```
function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
    PostRequest calldata request = incoming.request;
    if (!request.source.equals(IDispatcher(_host).hyperbridge())) revert UnauthorizedAction();
    OnAcceptActions action = OnAcceptActions(uint8(request.body[0]));
    if (action == OnAcceptActions.SetTiers) { ... }
    else if (action == OnAcceptActions.Withdraw) {
        // arbitrary token/native transfer to w.beneficiary
    }
}
```
There is no `_relayer` storage slot and no `_checkRelayer(incoming.relayer)` call anywhere in this contract, confirmed by a full read of the file [2](#0-1) .

Compare this to the exact same pattern in sibling modules, all of which gate `onAccept` on the delivering relayer before decoding the action:
- `HostManager.onAccept` uses `restrict(incoming.relayer, _params.admin)` [3](#0-2) 
- `ExtrinsicIntents.onAccept` calls `_checkRelayer(incoming.relayer)` before decoding governance actions [4](#0-3) 
- `BridgeToken.onAccept` calls `_checkRelayer(incoming.relayer)` before minting [5](#0-4) 
- `SimplexPaymaster.onAccept` calls `_checkRelayer(incoming.relayer)` immediately after `onlyHost` [6](#0-5) 

The project's own design decisions explicitly document *why* this gate is necessary: relaying is permissionless (anyone can call `HandlerV2.handlePostRequests`/`handleGetResponses` and the handler forwards `_msgSender()` unauthenticated as `incoming.relayer`), and if the host's `handler` is ever compromised or a consensus proof is forged, an attacker-controlled relayer can get an `onAccept` call invoked with a spoofed `request.source` that satisfies the naive `equals(hyperbridge)` check [7](#0-6) . The delivery flow doc confirms the relayer field is exactly `_msgSender()` with "no trusted forwarder" [8](#0-7) . This is precisely analogous to CVE-2017-12622: a privileged administrative code path (`gfsh` over HTTP) that omits an authorization check other paths enforce, letting an otherwise-unprivileged caller reach privileged cluster-management functionality. Here, `BandwidthManager` omits the relayer-authorization layer that every sibling governance handler enforces, letting an unprivileged relayer/caller reach privileged `Withdraw`/`SetTiers` functionality once the source check can be satisfied (forged consensus, compromised/malicious handler swap, or any bug that lets an untrusted party get a spoofed-source request delivered).

### Impact Explanation
- `OnAcceptActions.Withdraw` transfers an arbitrary `amount` of `w.token` (or native ETH) to an arbitrary `w.beneficiary` chosen by whoever controls the message body — concrete theft of all funds (fee-token and native) held by `BandwidthManager`.
- `OnAcceptActions.SetTiers` lets an attacker set `tierPrice` to arbitrary values (e.g. zero), enabling free/near-free bandwidth purchases, an economic griefing/theft vector against `pallet-bandwidth`'s revenue model.
- Because there is no independent relayer restriction, `BandwidthManager` has strictly weaker defense-in-depth than every comparable module in the same repository, despite guarding privileged fund-moving logic.

### Likelihood Explanation
Reaching this path requires either (a) a forged/compromised consensus proof that lets an attacker dispatch an arbitrary `PostRequest` with `source` spoofed to `hyperbridge`, or (b) the host's `handler`/consensus client being replaced by a malicious contract (the exact scenario the sibling contracts were specifically hardened against). While this is not a "no proof needed" bug, the codebase's own recent hardening history treats this threat model as realistic and worth defending against for every other module that holds funds or governance power — `BandwidthManager` was simply missed, making it the weak link.

### Recommendation
Add the same `_relayer` storage slot, `_checkRelayer(incoming.relayer)` gate (and a governance-only setter/`Execute`-style rotation path, or fold it into an `onlyHost`-gated action), mirroring `ExtrinsicIntents._checkRelayer` / `SimplexPaymaster._checkRelayer`, and call it in `BandwidthManager.onAccept` before decoding `OnAcceptActions`, exactly as done in `HostManager`, `ExtrinsicIntents`, `BridgeToken`, and `SimplexPaymaster`.

### Proof of Concept
1. Assume a scenario matching the threat model the sibling contracts were hardened against: the host's `handler` (or consensus client) is compromised/forged such that an attacker can get `EvmHost.dispatchIncoming` to invoke `BandwidthManager.onAccept` with a `PostRequest` whose `source` equals `hyperbridge` and whose `body` is `[Withdraw] ++ abi.encode(Withdrawal{token: feeToken, beneficiary: attacker, amount: fullBalance})`.
2. `onAccept` passes `onlyHost` (call originates from the real host) and `request.source.equals(hyperbridge)` (spoofed/forged content satisfies this).
3. No relayer check exists, so the action proceeds to `abi.decode` and executes `IERC20(w.token).safeTransfer(w.beneficiary, w.amount)`, draining the contract's balance to `attacker`.
4. Contrast with `HostManagerTest.testForgedHandlerSwapIsRefused` [9](#0-8)  and `ExtrinsicIntents`/`SimplexPaymaster` relayer-gate tests, which demonstrate the exact same delivery attempt is refused with `UnauthorizedAction`/`Unauthorized`/`UnauthorizedRelayer` in every other module — `BandwidthManager` has no equivalent test or guard, confirming the gap.

### Citations

**File:** evm/src/apps/BandwidthManager.sol (L1-233)
```text
// Copyright (C) Polytope Labs Ltd.
// SPDX-License-Identifier: Apache-2.0

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// 	http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
pragma solidity ^0.8.17;

import {Bytes} from "@polytope-labs/solidity-merkle-trees/src/trie/Bytes.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {IERC20Metadata} from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ERC165} from "@openzeppelin/contracts/utils/introspection/ERC165.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

import {PostRequest} from "@hyperbridge/core/libraries/Message.sol";
import {DispatchPost, IDispatcher} from "@hyperbridge/core/interfaces/IDispatcher.sol";
import {IncomingPostRequest, IApp} from "@hyperbridge/core/interfaces/IApp.sol";
import {HyperApp} from "@hyperbridge/core/apps/HyperApp.sol";

/// Wire payload dispatched by `purchase()` to `pallet-bandwidth`. The
/// pallet credits a tier-bucket on `chain` for `app`, scaled by `months`.
struct BandwidthPurchaseMsg {
    /// Recipient app whose bandwidth is being topped up.
    bytes app;
    /// Tier discriminant (matches `pallet_bandwidth::TierIndex`).
    uint256 tier;
    /// Number of tier-windows to credit. Bytes and duration both scale.
    uint256 months;
    /// UTF-8 chain id like `"EVM-8453"` or `"EVM-137"`.
    bytes chain;
}

/// One row of a `SetTiers` governance batch.
struct Tier {
    /// Tier discriminant (matches `pallet_bandwidth::TierIndex`).
    uint256 tier;
    /// Price in 18-decimal units; scaled at purchase time to fee-token decimals.
    uint256 price;
}

/// Payload of a `Withdraw` governance message — recovers `amount` of
/// `token` to `beneficiary`. `token` is named explicitly so stale
/// fee-token balances after a host-side swap can still be drained.
struct Withdrawal {
    address token;
    address beneficiary;
    uint256 amount;
}

/// @title BandwidthManager
/// @notice Per-chain prepaid bandwidth storefront. Buyers call
/// `purchase()` to debit a fee-token and dispatch a credit message to
/// `pallet-bandwidth` on hyperbridge; tier prices and treasury
/// withdrawals are governed exclusively by the pallet via `onAccept`.
contract BandwidthManager is HyperApp, ERC165, Ownable {
    using Bytes for bytes;
    using SafeERC20 for IERC20;

    /// Must equal `pallet-bandwidth`'s `PalletId`. The pallet enforces
    /// this on inbound messages, so changing it on either side breaks
    /// the round-trip.
    bytes public constant PALLET_BANDWIDTH_MODULE_ID = bytes("BWMARKET");

    /// Must equal the bound on `pallet_bandwidth::AppKey`. The pallet rejects anything longer,
    /// so checking here fails the purchase before the payer is charged for a message that
    /// cannot be credited.
    uint256 public constant MAX_APP_LENGTH = 32;

    /// Discriminants for the first byte of an `onAccept` body. Order
    /// must match `pallet_bandwidth::lib.rs::ACTION_*`.
    enum OnAcceptActions {
        SetTiers,
        Withdraw
    }

    // The host address
    address public _host;

    /// tier → price in 18-decimal units. Zero = unconfigured (purchases
    /// against an unconfigured tier revert with `UnknownTier`).
    mapping(uint256 => uint256) public tierPrice;

    /// Emitted on a successful `purchase()`. `commitment` is the
    /// hyperbridge dispatch commitment so callers can correlate with
    /// the pallet-side credit event.
    event BandwidthPurchased(
        address indexed payer,
        address feeToken,
        uint256 tier,
        uint256 months,
        uint256 amountPaid,
        bytes app,
        bytes chain,
        bytes32 commitment
    );
    /// Emitted once per tier in a `SetTiers` governance batch.
    event TierSet(uint256 indexed tier, uint256 price18d);
    /// Emitted by a `Withdraw` governance message after the transfer succeeds.
    event Withdrawn(address indexed token, address indexed beneficiary, uint256 amount);

    /// `app`/`chain` empty, or `months == 0`.
    error InvalidPurchase();
    /// Tier price not configured (`tierPrice[tier] == 0`).
    error UnknownTier();
    /// 18-d tier price doesn't divide cleanly into `feeToken()` decimals.
    error PriceNotRepresentable();
    /// `onAccept` body came from a non-hyperbridge source, or the
    /// action discriminant is out of range.
    error UnauthorizedAction();
    /// Insufficient native token balance to cover the withdrawal amount.
    error InsufficientNativeToken();

    constructor(address owner) Ownable(owner) {}

    /// @inheritdoc HyperApp
    function host() public view override returns (address) {
        return _host;
    }

    /*
    * @notice Sets the host address on the bandwidth manager.
    * @param hostAddr The new host address.
    */
    function setHost(address hostAddr) public onlyOwner {
        if (_host != address(0)) revert UnauthorizedAction();
        _host = hostAddr;
    }

    /// @inheritdoc ERC165
    function supportsInterface(bytes4 interfaceId) public view virtual override returns (bool) {
        return interfaceId == type(IApp).interfaceId || super.supportsInterface(interfaceId);
    }

    /// @notice Pay for `months` of `tier` bandwidth on `chain` for `app`.
    /// @dev Pulls the scaled tier price from `msg.sender` in the host's
    /// fee token, then dispatches a `BandwidthPurchaseMsg` to
    /// `pallet-bandwidth` on hyperbridge. The pallet credits an
    /// `(chain, app)` bucket bounded by tier `bytes` × `months`.
    /// @param app Recipient app address (usually 20-byte EVM, packed as bytes).
    /// @param tier Tier discriminant; must be configured via `SetTiers`.
    /// @param months Number of tier-windows to credit; must be > 0.
    /// @param chain UTF-8 chain id (e.g. `"EVM-8453"`) of the credit chain.
    /// @return commitment Hyperbridge dispatch commitment for tracking.
    function purchase(bytes calldata app, uint256 tier, uint256 months, bytes calldata chain)
        external
        returns (bytes32 commitment)
    {
        if (app.length == 0 || app.length > MAX_APP_LENGTH || chain.length == 0 || months == 0) {
            revert InvalidPurchase();
        }
        uint256 price18d = tierPrice[tier];
        if (price18d == 0) revert UnknownTier();

        uint256 total18d = price18d * months;
        address feeToken = IDispatcher(_host).feeToken();
        uint8 dec = IERC20Metadata(feeToken).decimals();
        uint256 scale = 10 ** (18 - dec);
        if (total18d % scale != 0) revert PriceNotRepresentable();
        uint256 amount = total18d / scale;

        IERC20(feeToken).safeTransferFrom(msg.sender, address(this), amount);

        BandwidthPurchaseMsg memory body = BandwidthPurchaseMsg({
            app: app,
            tier: tier,
            months: months,
            chain: chain
        });

        commitment = IDispatcher(_host).dispatch(
            DispatchPost({
                dest: IDispatcher(_host).hyperbridge(),
                to: PALLET_BANDWIDTH_MODULE_ID,
                body: abi.encode(body),
                timeout: 0,
                fee: 0,
                payer: address(this)
            })
        );

        emit BandwidthPurchased({
            payer: msg.sender,
            feeToken: feeToken,
            tier: tier,
            months: months,
            amountPaid: amount,
            app: app,
            chain: chain,
            commitment: commitment
        });
    }


    /// @notice Inbound governance from `pallet-bandwidth`. The first
    /// body byte selects `OnAcceptActions`; the remainder is the
    /// action's ABI-encoded payload.
    /// @dev Only the configured host may invoke (`onlyHost`); the
    /// request's `source` must additionally equal hyperbridge.
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        PostRequest calldata request = incoming.request;

        if (!request.source.equals(IDispatcher(_host).hyperbridge())) revert UnauthorizedAction();

        OnAcceptActions action = OnAcceptActions(uint8(request.body[0]));
        if (action == OnAcceptActions.SetTiers) {
            Tier[] memory updates = abi.decode(request.body[1:], (Tier[]));
            for (uint256 i = 0; i < updates.length; i++) {
                tierPrice[updates[i].tier] = updates[i].price;
                emit TierSet(updates[i].tier, updates[i].price);
            }
        } else if (action == OnAcceptActions.Withdraw) {
            Withdrawal memory w = abi.decode(request.body[1:], (Withdrawal));
            if (w.token != address(0)) {
                IERC20(w.token).safeTransfer(w.beneficiary, w.amount);
            } else {
                (bool sent,) = w.beneficiary.call{value: w.amount}("");
                if (!sent) revert InsufficientNativeToken();
            }
            emit Withdrawn(w.token, w.beneficiary, w.amount);
        } else {
            revert UnauthorizedAction();
        }
    }
}
```

**File:** evm/src/core/HostManager.sol (L134-142)
```text
    function onAccept(IncomingPostRequest calldata incoming)
        external
        override
        restrict(msg.sender, _params.host)
        restrict(incoming.relayer, _params.admin)
    {
        PostRequest calldata request = incoming.request;
        // Only the Hyperbridge parachain can send requests to this module.
        if (!request.source.equals(IHost(_params.host).hyperbridge())) revert UnauthorizedAction();
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L331-340)
```text
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }

        // only hyperbridge is permitted to perform these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
```

**File:** evm/src/apps/BridgeToken.sol (L88-92)
```text
    /// @dev Gated on the relayer before the base token mints. See `_checkRelayer`.
    function onAccept(IncomingPostRequest calldata incoming) public override onlyHost {
        _checkRelayer(incoming.relayer);
        super.onAccept(incoming);
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L313-317)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) {
            revert UnauthorizedCall();
        }
```

**File:** sdk/packages/core/docs/ai/decisions/2026-09-03-hostmanager-deliveries-are-gated-too-and-that-does-not-touch.md (L1-14)
```markdown
# 2026-09-03 — `HostManager` deliveries are gated too, and that does not touch permissionless relaying

Chosen: `HostManager.onAccept` refuses any relayer but the one the host admin set, zero included.

The app gates check an address the host reports, and the host takes it from its handler. The
handler is a host parameter that a `SetHostParam` governance message can replace, and until now
any relayer could deliver that message once its consensus proof verified. Under a forged consensus
an attacker would swap in a handler that reports the whitelisted relayer on every message, and the
app gates would pass. Gating the HostManager closes that route.

It does not weaken the open-relayer model because the HostManager never carries user traffic. Its
first check already rejects anything not sourced from Hyperbridge, so the only messages it ever
sees are Polytope's own `Withdraw` and `SetHostParam`. Third-party relayers keep delivering every
ordinary message to every ordinary app exactly as before.
```

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L7-17)
```markdown
1. A relayer calls `HandlerV2.handlePostRequests` (or `handleGetResponses`). After proof
   verification the handler calls `host.dispatchIncoming(request, _msgSender())`. `_msgSender()` is
   plain `msg.sender`; the handler has no trusted forwarder.
2. `EvmHost.dispatchIncoming` (restricted to the handler) writes a receipt for the request
   commitment, then low-level calls the module with `IApp.onAccept(IncomingPostRequest(request,
   relayer))`. If that call fails the host deletes the receipt and returns without reverting, so the
   rest of the batch proceeds and the message stays deliverable.
3. `ExtrinsicIntents.onAccept` runs `onlyHost`, then `_checkRelayer(incoming.relayer)`, which reverts
   with `Unauthorized` when a relayer is set and the delivery is from anyone else. Only then is the
   first body byte read as a `RequestKind`. `onGetResponse` has the same two steps before touching
   the response.
```

**File:** evm/tests/foundry/HostManagerTest.sol (L225-241)
```text
    function testForgedHandlerSwapIsRefused() public {
        MaliciousHandler malicious = new MaliciousHandler();
        HostParams memory params = host.hostParams();
        address honestHandler = params.handler;
        params.handler = address(malicious);
        PostRequest memory swap = _setHostParamRequest(params);

        // Delivered by the attacker (through the honest handler, proof assumed forged).
        vm.prank(address(handler));
        host.dispatchIncoming(swap, OUTSIDER);
        assertEq(host.hostParams().handler, honestHandler, "handler unchanged");

        // The attacker's contract is not the handler, so it cannot inject a relayer address.
        PostRequest memory forged = _setHostParamRequest(host.hostParams());
        vm.expectRevert(EvmHost.UnauthorizedAction.selector);
        malicious.deliver(EvmHost(payable(address(host))), forged, address(this));
    }
```
