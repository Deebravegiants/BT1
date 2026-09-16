### Title
IntentGatewayV2 escrow cannot be paused, leaving user funds unprotected against a compromised dependency or discovered logic bug - (File: evm/src/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2` is the unprivileged, user-facing entry point that escrows user funds via `placeOrder`, releases them via `fillOrder`, and refunds them via `cancelOrder`. Unlike every other value-holding contract in this codebase — `EvmHost` (frozen/notFrozen), `HandlerV2` (notFrozen), `HyperFungibleToken`/`HyperFungibleTokenUpgradeable` (Pausable), and `HyperbridgeLzEndpoint` (Pausable) — `IntentGatewayV2` has no pause mechanism at all, so the admin has no way to halt new escrow deposits or fills if the contract's dependencies (the Uniswap V2 router it swaps through, the ISMP host/relayer path it settles through, or its own logic) are found to be exploitable.

### Finding Description
`IntentGatewayV2` declares `_owner` as "Privileged admin for future upgrade-gated actions (e.g. pausing)" but this admin is never wired to any pause guard: [1](#0-0) 

Grepping the app for `pause`/`Pausable`/`whenNotPaused` confirms `IntentGatewayV2.sol` and its base contracts `IntrinsicIntents`/`ExtrinsicIntents` contain no such logic, whereas `BridgeToken.sol` and `IntentsBase.sol` matches are unrelated occurrences elsewhere in the codebase; `_owner` itself has no other reference beyond its declaration and constructor assignment.

Every unprivileged, fund-moving entry point is reachable with zero access control:
- `placeOrder` escrows arbitrary ERC20/native tokens from any caller, swaps native token for the fee token via an external Uniswap V2 router, and credits `_orders[commitment][token]`: [2](#0-1) [3](#0-2) 
- `fillOrder` releases escrowed inputs to a solver and, for cross-chain orders, dispatches a settlement message through the ISMP host: [4](#0-3) 
- `cancelOrder` refunds escrow directly (same-chain) or via an ISMP round trip (cross-chain): [5](#0-4) 

None of these functions are gated by a pause modifier, so if the Uniswap V2 router integration, the `IDispatcher`/host it settles through, the solver-selection/EIP-712 logic, or any yet-undiscovered logic bug in the escrow accounting is compromised, the admin cannot stop new deposits (`placeOrder`) or draining fills (`fillOrder`) — the exact bug class described in the external report ("if Perp/Rage Trade are compromised, the Owner has no way of stopping further loss of user funds"). Here, the analogous externally-reachable dependencies are the Uniswap V2 router and the ISMP settlement path, both directly invoked by an unprivileged caller's single transaction.

This contrasts with the rest of the protocol's design intent: `EvmHost`/`HandlerV2` implement a `FrozenStatus`-based circuit breaker specifically so governance can halt dispatch/delivery under compromise, and `HyperFungibleToken` explicitly documents Pausable as the mechanism to "use ... for emergency situations": [6](#0-5) [7](#0-6) 

`IntentGatewayV2` — which directly escrows and moves user funds on every chain it is deployed to — has no equivalent safeguard.

### Impact Explanation
If a vulnerability is found in `IntentGatewayV2`'s escrow, fee-swap, or cross-chain settlement logic (or in an external dependency it calls, such as the Uniswap V2 router), the admin has no way to stop new orders from being placed or existing escrow from being drained through `fillOrder`/`cancelOrder` while a fix is prepared and an upgrade is rolled out. Given the contract holds live user escrow across every deployment, this is a protocol-wide inability to prevent an ongoing, unpriviledged loss-of-funds event once a bug class becomes known — this qualifies as Medium severity per the same reasoning as the underlying report (loss of user funds when a reachable dependency/logic path is compromised, with no owner recourse).

### Likelihood Explanation
`IntentGatewayV2` is upgradeable (`Initializable`, proxy-based per the migration/version logic in the contract) and reachable by any address in a single transaction via `placeOrder`. The likelihood of this gap actually causing loss depends on some other bug or dependency compromise materializing first (e.g., in the Uniswap V2 fee-swap path, solver-selection signature checks, or cross-chain settlement), but given the contract's broad attack surface (predispatch/postdispatch calldata execution via `CallDispatcher`, EIP-712 solver selection, cross-chain proof verification), the absence of an emergency stop meaningfully raises the consequence of any future discovered bug from "urgent patch" to "unstoppable drain until upgrade lands."

### Recommendation
Add a pause mechanism (e.g., OpenZeppelin's `PausableUpgradeable`, consistent with `HyperFungibleTokenUpgradeable`) to `IntentGatewayV2`, gated by the existing `_owner` admin. Guard `placeOrder` (new escrow deposits) and, at minimum, `fillOrder`'s cross-chain leg and any external-router-dependent code paths with `whenNotPaused`, while ensuring `cancelOrder`/refund paths remain callable when paused so users can always recover already-escrowed funds. This mirrors the design already used for `EvmHost`'s `FrozenStatus` and `HyperFungibleToken`'s `Pausable`.

### Proof of Concept
Not applicable as an exploit PoC — this is an availability/circuit-breaker gap rather than a directly exploitable primitive. Structural evidence:
1. `_owner` is documented as reserved for "future upgrade-gated actions (e.g. pausing)" but is not used to gate any function: [1](#0-0) 
2. `placeOrder`, `fillOrder`, and `cancelOrder` have no pause/frozen guard of any kind, unlike `EvmHost.dispatch` (`notFrozen`) and `HyperFungibleToken.send`/`onAccept` (`whenNotPaused`): [8](#0-7) [9](#0-8) [10](#0-9) [11](#0-10)

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L63-74)
```text
    /// @dev Privileged admin for future upgrade-gated actions (e.g. pausing). Immutable, so it must
    /// be identical across chains or the deterministic proxy address diverges. Does not gate
    /// `initialize`; atomic CREATE2 deployment already binds the init data to the canonical address.
    address public immutable _owner;

    /// @dev Sets the EIP-712 domain ("IntentGateway", "2"), records the admin, and locks this raw
    /// implementation against direct initialization.
    /// @param owner The privileged admin address.
    constructor(address owner) EIP712("IntentGateway", "2") {
        if (owner == address(0)) revert InvalidInput();
        _owner = owner;
        _disableInitializers();
```

**File:** evm/src/apps/IntentGatewayV2.sol (L194-234)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();

        // Reject duplicate output tokens
        uint256 outputsLen_ = order.output.assets.length;
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                if tload(token) {
                    mstore(0, 0xb4fa3fb3) // InvalidInput.selector
                    revert(0x1c, 0x04)
                }
                tstore(token, 1)
            }
            unchecked {
                ++i;
            }
        }
        // Clean up transient storage so repeated placeOrder calls in the same tx don't false-positive.
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                tstore(token, 0)
            }
            unchecked {
                ++i;
            }
        }

        address hostAddr = host();
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        uint256 inputsLen = order.inputs.length;

        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
```

**File:** evm/src/apps/IntentGatewayV2.sol (L375-392)
```text
        if (order.fees > 0) {
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = feeToken;
                uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
                msgValue -= amounts[0];
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

            _orders[commitment][TRANSACTION_FEES] = order.fees;
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L443-483)
```text
    function fillOrder(Order calldata order, FillOptions calldata options) public payable nonReentrant {
        uint256 blockNumber = _blockNumber();
        if (order.deadline < blockNumber) revert Expired();
        // The solver's own bound on how long its quoted price stands. Zero means unbounded,
        // which is the right default for a solver filling directly — it is only at risk from
        // its own staleness. It matters for a bid signed through the coprocessor, where the
        // order placer chooses the moment of execution and nothing else caps the wait.
        if (options.validUntil != 0 && blockNumber > options.validUntil) revert FillExpired();
        bytes32 commitment = keccak256(abi.encode(order));

        address hostAddr = host();
        bytes32 currentChain = keccak256(IDispatcher(hostAddr).host());
        bytes32 orderSource = keccak256(order.source);
        bytes32 orderDest = keccak256(order.destination);
        bool isSameChain = orderSource == orderDest;

        if (isSameChain && orderSource != currentChain) revert WrongChain();
        if (!isSameChain && orderDest != currentChain) revert WrongChain();

        if (_filled[commitment] != address(0)) revert Filled();

        if (_params.solverSelection) {
            bytes32 storedSelectionHash;
            assembly {
                storedSelectionHash := tload(commitment)
            }

            bytes32 expectedSelectionHash = keccak256(abi.encode(msg.sender, order.session));
            if (storedSelectionHash != expectedSelectionHash) revert Unauthorized();
        }

        uint256 outputsLen = order.output.assets.length;
        if (options.outputs.length != outputsLen) revert InvalidInput();
        if (order.inputs.length != outputsLen) revert InvalidInput();

        if (isSameChain) {
            _fillSameChain(order, options, commitment);
        } else {
            _fillCrossChain(order, options, commitment);
        }
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L505-537)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable nonReentrant {
        bytes32 commitment = keccak256(abi.encode(order));

        if (_filled[commitment] != address(0)) revert Filled();

        address hostAddr = host();
        bytes32 currentChain = keccak256(IDispatcher(hostAddr).host());
        bytes32 orderSource = keccak256(order.source);
        bytes32 orderDest = keccak256(order.destination);
        bool isSameChain = orderSource == orderDest;

        // Emitted here, once, rather than from each of the three routes below. Every check those
        // routes make — Unauthorized, NotExpired, UnknownOrder — reverts, and a revert discards
        // logs, so an early emit can never announce a cancellation that did not happen. Emitting
        // before the branch also keeps `EscrowRefunded` the last log on the same-chain route, where
        // the refund is processed in this same transaction. Three emit sites cost bytecode this
        // contract does not have: it sits within ~100 bytes of the EIP-170 limit.
        emit OrderCancelled({commitment: commitment, canceller: msg.sender});

        if (isSameChain) {
            // Checked here rather than inside `_cancelSameChain`, which used to re-read `host()`,
            // re-query the host's state machine id and re-hash `order.source` to reach the same
            // answer this function already has. Same check, one external call fewer.
            if (currentChain != orderSource) revert WrongChain();
            _cancelSameChain(order, commitment);
        } else if (currentChain == orderSource) {
            _cancelFromSource(order, options, commitment);
        } else if (currentChain == orderDest) {
            _cancelFromDest(order, options, commitment);
        } else {
            revert WrongChain();
        }
    }
```

**File:** evm/src/core/EvmHost.sol (L339-357)
```text
    // The IsmpHost has been frozen and cannot dispatch requests
    error FrozenHost();

    // Cannot change the fee token without sweeping all funds from previous one
    error CannotChangeFeeToken();

    // restricts call to the provided `caller`
    modifier restrict(address caller) {
        if (_msgSender() != caller) revert UnauthorizedAction();
        _;
    }

    /*
     * @dev Check if outgoing messages are permitted
     */
    modifier notFrozen() {
        if (_frozen == FrozenStatus.Outgoing || _frozen == FrozenStatus.All) revert FrozenHost();
        _;
    }
```

**File:** evm/src/core/EvmHost.sol (L921-921)
```text
    function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L132-141)
```text
## Pausability

Both contracts inherit from OpenZeppelin's `Pausable`. The owner can pause and unpause all operations:

```solidity lineNumbers
IHyperFungibleToken(tokenAddress).pause();
IHyperFungibleToken(tokenAddress).unpause();
```

When paused, `HyperFungibleToken` blocks all ERC20 transfers (`transfer` and `transferFrom`) in addition to cross-chain `send()` and `onAccept()`. This is a full stop on all token movement — use it for emergency situations or during migrations.
```
