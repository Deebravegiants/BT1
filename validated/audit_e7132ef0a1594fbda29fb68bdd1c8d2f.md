## Finding: Tron `IntentGatewayV2` lacks the relayer-allowlist gate present in the EVM implementation

The CVE describes a permission check enforced on one path (the standard ticket view) but bypassable through an alternate path (ticket detail view) that reaches the same underlying data/action. The Hyperbridge codebase has a directly analogous split: the EVM `IntentGatewayV2`/`ExtrinsicIntents` callback path enforces a relayer allowlist before processing any inbound Hyperbridge delivery, but the parallel Tron implementation of the same contract omits that gate entirely, even though both are reached through the same permissionless dispatch/relay mechanism.

### Title
Tron `IntentGatewayV2.onAccept` omits the relayer-allowlist gate enforced on the EVM implementation, allowing any relayer to trigger privileged callback paths - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
On EVM, `ExtrinsicIntents.onAccept` and `onGetResponse` call `_checkRelayer(incoming.relayer)` before decoding any request body, restricting delivery to a single authorised relayer once one is armed. On Tron, the equivalent `IntentGatewayV2.onAccept` has no `_relayer` state, no `_checkRelayer`, and no `setRelayer`/`migrate` machinery at all — every `RequestKind` (including `NewDeployment`, `UpdateParams`, `SweepDust`, and escrow redemption/refund) is reachable by any relayer that can get a valid ISMP delivery through the host.

### Finding Description
`HandlerV2.handlePostRequests`/`handleGetResponses` are permissionless — any address can submit a valid proof and become the `relayer` argument passed into `host.dispatchIncoming(...)` [1](#0-0) . On the canonical EVM gateway, this is mitigated by a relayer allowlist checked first in the callback: `ExtrinsicIntents.onAccept` runs `_checkRelayer(incoming.relayer)` before reading any part of the request body, and the same gate is enforced in `onGetResponse` [2](#0-1) . This gate was deliberately added to cover "escrow redemptions, refunds and every governance action, upgrades included" [3](#0-2) .

The Tron port of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, has no `_relayer` field, no `_checkRelayer`, and no `setRelayer`/`migrate` functions anywhere in the file [4](#0-3) . Its `onAccept` goes straight from decoding the `RequestKind` byte to dispatching each case — `RedeemEscrow`/`RefundEscrow` via `authenticate()`, and `NewDeployment`/`UpdateParams`/`SweepDust` gated only by a Hyperbridge-source check, with no relayer restriction at any point [5](#0-4) .

### Impact Explanation
Because the relayer allowlist is entirely absent on Tron, the protection the EVM fix was designed to provide — restricting who may trigger the gateway's callback logic once a relayer is armed — does not exist for the Tron deployment. Any address capable of relaying a valid ISMP proof through the permissionless `HandlerV2`/host delivery path can trigger `onAccept` for governance-carrying `RequestKind`s (`NewDeployment`, `UpdateParams`, `SweepDust`) and escrow release/refund flows, none of which can be excluded the way the EVM gateway excludes non-allowlisted relayers. This is a concrete unauthorized-app-action condition: a code path that on one chain requires a specific authorised principal is, on another chain running materially the same application logic, reachable by any unprivileged relayer.

### Likelihood Explanation
`HandlerV2.handlePostRequests`/`handleGetResponses` are explicitly "Permissionless (can be called by anyone)" [6](#0-5) , so any party that can obtain a valid Hyperbridge proof for a pending message (which they do not need special standing to submit) can act as the "relayer" for that delivery. Since the Tron contract performs no relayer check, this requires no special access beyond what any ordinary relayer already has.

### Recommendation
Port the `_relayer`/`_checkRelayer`/`setRelayer`/`migrate` mechanism from `evm/src/apps/intentsv2/ExtrinsicIntents.sol` and `IntentsBase` into `evm/tron/contracts/apps/IntentGatewayV2.sol`, gating `onAccept` and `onGetResponse` the same way, and audit other Tron-specific contract copies for the same class of drift from the EVM security baseline.

### Proof of Concept
1. Deploy/observe the Tron `IntentGatewayV2` as shipped (no `_relayer` state exists to arm).
2. Any address submits a valid Hyperbridge proof for a pending `UpdateParams`/`NewDeployment`/`SweepDust` (or `RedeemEscrow`/`RefundEscrow`) request via the permissionless handler, becoming the `relayer` in `dispatchIncoming`.
3. `onAccept` processes the request with no relayer check at all (contrast with `evm/tests/foundry/IntentGatewayV2Test.sol::testOnAcceptRejectsUnlistedRelayer`, which proves the EVM version reverts an unlisted relayer with `Unauthorized`) [7](#0-6) ; no equivalent test or gate exists for the Tron contract.

### Citations

**File:** evm/src/core/HandlerV2.sol (L181-210)
```text
    function handlePostRequests(IHost host, PostRequestMessage calldata request) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(request.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        uint256 requestsLen = request.requests.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](requestsLen);

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // check destination
            if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
            // check time-out
            if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.request.hash());
        }

        bytes32 root = host.stateMachineCommitment(request.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, request.proof.multiproof, leaves, request.proof.leafCount);
        if (!valid) revert InvalidProof();

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-366)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }

        // only hyperbridge is permitted to perform these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
        if (kind == RequestKind.NewDeployment) {
            _addDeployment(abi.decode(incoming.request.body[1:], (Deployment)));
        } else if (kind == RequestKind.UpdateParams) {
            _updateParams(abi.decode(incoming.request.body[1:], (ParamsUpdate)));
        } else if (kind == RequestKind.SweepDust) {
            _sweepDust(abi.decode(incoming.request.body[1:], (SweepDust)));
        } else if (kind == RequestKind.Execute) {
            Address.functionDelegateCall(ERC1967Utils.getImplementation(), incoming.request.body[1:]);
        }
    }

    /**
     * @dev Handles the response to a Hyperbridge GET request dispatched during
     * `_cancelFromSource`. Verifies that the `_filled` storage slot on the destination
     * chain is empty (meaning the order was never filled), then refunds the escrowed
     * tokens to the original user. Reverts with `Filled` if the slot is non-empty.
     *
     * @param incoming The incoming GET response from Hyperbridge containing the storage proof.
     */
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
```

**File:** sdk/packages/core/docs/ai/changelog/2026-09-03-relayer-allowlist-on-the-intent-gateway.md (L1-10)
```markdown
# 2026-09-03 — Relayer allowlist on the intent gateway

The gateway now accepts `onAccept` and `onGetResponse` deliveries only from a single authorised
relayer stored at `_relayer` (slot 13, packed behind `_paused`). The check runs before the message
body is decoded, so escrow redemptions, refunds and every governance action, upgrades included, are
covered. A refused delivery reverts, which the host records as undelivered, so the authorised
relayer can submit the same message later. `setRelayer(address)` is callable by the immutable
`_owner` and by the host; the host branch exists so a governance `UpgradeContract` can carry the
call as its migration calldata and arm the relayer in the upgrade transaction (`upgradeToAndCall`
delegatecalls that calldata with the host still as `msg.sender`).
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L55-120)
```text
contract IntentGatewayV2 is HyperApp, EIP712 {
    using SafeERC20 for IERC20;

    /**
     * @dev EIP-712 type hash for SelectSolver message
     */
    bytes32 public constant SELECT_SOLVER_TYPEHASH = keccak256("SelectSolver(bytes32 commitment,address solver)");

    /**
     * @dev Enum representing the different kinds of incoming requests that can be executed.
     */
    enum RequestKind {
        /// @dev Identifies a request for redeeming an escrow.
        RedeemEscrow,
        /// @dev Identifies a request for recording new contract deployments
        NewDeployment,
        /// @dev Identifies a request for updating parameters.
        UpdateParams,
        /// @dev Identifies a request for sweeping accumulated dust
        SweepDust,
        /// @dev Identifies a request for refunding an escrow (cancellation from destination chain)
        RefundEscrow
    }

    /**
     * @dev Address constant for transaction fees, derived from the keccak256 hash of the string "txFees".
     * This address is used to store or reference the transaction fees within the contract.
     */
    address private constant TRANSACTION_FEES = address(uint160(uint256(keccak256("txFees"))));

    /**
     * @notice Constant representing a filled slot in big endian format
     * @dev Hex value 0x06 padded with leading zeros to fill 32 bytes
     */
    bytes32 constant FILLED_SLOT_BIG_ENDIAN_BYTES =
        hex"0000000000000000000000000000000000000000000000000000000000000002";

    /**
     * @dev Mapping to store the addresses associated with filled intents.
     * The key is a bytes32 hash representing the intent, and the value is the address
     * that filled the intent.
     */
    mapping(bytes32 => address) public _filled;

    /**
     * @dev Private variable to store the nonce value.
     * This nonce is used to ensure the uniqueness of orders.
     */
    uint256 public _nonce;

    /**
     * @dev Private variable to store the parameters for the IntentGateway module.
     * This variable is of type `Params` and is used internally within the contract.
     */
    Params private _params;

    /**
     * @dev Address of the admin, which can initialize the contract.
     * The admin is reset to the zero address after initialization.
     */
    address private _admin;

    /**
     * @dev Mapping to store orders.
     * The outer mapping key is a bytes32 value representing the order commitment.
     * The inner mapping key is an address representing the escrowed token contract.
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-683)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }

        // only hyperbridge is permitted to perfom these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
        if (kind == RequestKind.NewDeployment) {
            NewDeployment memory body = abi.decode(incoming.request.body[1:], (NewDeployment));
            _instances[keccak256(body.stateMachineId)] = body.gateway;

            emit NewDeploymentAdded({stateMachineId: body.stateMachineId, gateway: body.gateway});
        } else if (kind == RequestKind.UpdateParams) {
            // Decode the body which includes optional destination-specific protocol fee updates
            ParamsUpdate memory update = abi.decode(incoming.request.body[1:], (ParamsUpdate));
            emit ParamsUpdated({previous: _params, current: update.params});
            _params = update.params;

            // Update destination-specific protocol fees if provided
            for (uint256 i; i < update.destinationFees.length;) {
                bytes32 stateMachineId = update.destinationFees[i].stateMachineId;
                uint256 feeBps = update.destinationFees[i].destinationFeeBps;
                _destinationProtocolFees[stateMachineId] = feeBps;

                unchecked {
                    ++i;
                }
                emit DestinationProtocolFeeUpdated(stateMachineId, feeBps);
            }
        } else if (kind == RequestKind.SweepDust) {
            SweepDust memory req = abi.decode(incoming.request.body[1:], (SweepDust));

            uint256 outputsLen = req.outputs.length;
            for (uint256 i; i < outputsLen;) {
                TokenInfo memory info = req.outputs[i];
                address token = address(uint160(uint256(info.token)));
                uint256 amount = info.amount;

                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
                unchecked {
                    ++i;
                }
                emit DustSwept(token, amount, req.beneficiary);
            }
        }
    }
```

**File:** docs/content/developers/evm/api/ihandler.mdx (L101-101)
```text
**Access:** Permissionless (can be called by anyone)
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L4461-4476)
```text
    function testOnAcceptRejectsUnlistedRelayer() public {
        (PostRequest memory request, bytes32 commitment, uint256 amount) = _escrowedRedeemRequest();

        vm.prank(address(host));
        vm.expectRevert(IntentsBase.Unauthorized.selector);
        intentGateway.onAccept(IncomingPostRequest({relayer: filler, request: request}));
        assertEq(intentGateway._orders(commitment, address(usdc)), amount, "escrow untouched");
        assertEq(intentGateway._filled(commitment), address(0), "order not finalised");

        // The very same message goes through once the authorised relayer submits it.
        uint256 before = usdc.balanceOf(filler);
        vm.prank(address(host));
        intentGateway.onAccept(IncomingPostRequest({relayer: relayer, request: request}));
        assertEq(usdc.balanceOf(filler) - before, amount, "authorised relayer releases escrow");
        assertEq(intentGateway._filled(commitment), filler, "order finalised");
    }
```
