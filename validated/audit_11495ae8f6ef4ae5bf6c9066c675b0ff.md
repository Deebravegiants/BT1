## Title
Non-standard token balance-vs-counter desync in `IntentGatewayV2.placeOrder` (Tron variant) - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

## Summary
The Lido report describes an internal accounting counter (`lidoLockedETH`) that is incremented by a *nominal requested amount* while the actual token balance moved can differ (due to token-specific quirks such as fee-on-transfer, rebasing, or wei-rounding). This causes the vault's `totalAssets()`-derived share price to diverge from the real backing, letting early depositors extract more value than later ones — a permanent-funds-freezing/unfair-distribution class bug. `evm/tron/contracts/apps/IntentGatewayV2.sol::placeOrder` contains the same root-cause pattern: it credits the escrow ledger (`_orders[commitment][token]`) with the *nominal* `reducedInputs[i].amount` instead of the amount actually verified to have arrived, for a token whose transfer semantics can differ from a plain ERC-20 (fee-on-transfer / rebasing / non-standard tokens are common on Tron, e.g. some TRC-20/USDT-like tokens have historically supported fee-on-transfer switches).

## Finding Description
In the mainline EVM `IntentGatewayV2.sol`, `placeOrder` was explicitly hardened against this exact bug class: it snapshots `balanceOf` before and after each transfer/sweep and mutates `order.inputs[i].amount` to the *actually received* amount before computing the commitment and crediting escrow [1](#0-0) , and this fix is verified by dedicated fee-on-transfer tests [2](#0-1) .

The Tron deployment of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, does **not** carry this fix. In both the predispatch and non-predispatch branches of `placeOrder`, the escrow ledger is credited with the pre-computed `reducedInputs[i].amount` (derived purely from `order.inputs[i].amount`, the caller-declared nominal amount minus protocol fee) — not from a measured balance delta:

```solidity
// predispatch branch
uint256 dust = balance - requiredAmount;
if (dust > 0) emit DustCollected(token, dust);
// Store reduced amount (after protocol fees) in escrow
_orders[commitment][token] += reducedInputs[i].amount;
``` [3](#0-2) 

```solidity
// non-predispatch branch
IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
// Store reduced amount (after protocol fees) in escrow
_orders[commitment][token] += reducedInputs[i].amount;
``` [4](#0-3) 

If the input token has any transfer-amount-reducing behavior (fee-on-transfer, deflationary burn-on-transfer, or a rounding/rebasing quirk analogous to Lido's 1-2 wei corner case), the gateway will hold strictly less of the token than `_orders[commitment][token]` claims it escrowed. This is exactly the Lido pattern: an internal accounting counter (`lidoLockedETH` / `_orders[commitment][token]`) is incremented by the *declared* amount rather than the *measured* amount actually held after the transfer, causing the accounting ledger to overstate real backing.

The non-predispatch branch's `dust` computation in the predispatch branch (`dust = balance - requiredAmount`) only detects *excess* balance (dust from over-transfers), not a shortfall — there is no `balance < requiredAmount` recheck after the sweep that would catch an under-delivery from a fee-taking token; the `if (balance < requiredAmount) revert(...)` check happens *before* the token is actually pulled into `address(this)` (it checks the dispatcher's balance, then blindly trusts `requiredAmount` when writing the escrow entry, never re-reading `IERC20(token).balanceOf(address(this))` after the sweep completes).

## Impact Explanation
This is reachable by any ordinary user calling `placeOrder` on the Tron IntentGateway with a fee-on-transfer or similarly non-conformant TRC-20 token as an input asset — no privileged role required. The resulting over-credited escrow entry means:
- The gateway's on-chain token balance is insufficient to fully honor `_orders[commitment][token]` for every input token across all outstanding orders once such a token is used, since the ledger claims more than what physically arrived.
- A solver who fills the order (or the user who cancels it) can be shorted, or — because escrow accounting is shared per-commitment/per-token across the whole gateway — other users' escrowed balances for the same token can become undercollateralized, since the gateway's real token balance is the sole backing for all `_orders[...]` entries for that token.
- This matches the reported impact class: permanent freezing of funds / unfair distribution, because once the ledger diverges from actual balance, some order participants cannot be paid in full from the gateway's actual holdings.

## Likelihood Explanation
Likelihood is moderate-to-high on Tron specifically because TRC-20/TRC-10 tokens (and even wrapped or migrated ERC-20-style tokens bridged to Tron) are more likely than mainnet ERC-20s to implement fee-on-transfer, blacklist/burn-on-transfer, or non-standard rounding behavior. Any user (not privileged) can trigger the vulnerable code path simply by placing an order with such a token as `order.inputs[i].token`; no special permissions, governance, or admin action is needed — the gateway's `predispatch`/non-predispatch code paths are called directly by `placeOrder`, which is `public payable` and open to any caller.

## Recommendation
Port the fix already present in the mainline `evm/src/apps/IntentGatewayV2.sol` to the Tron variant: snapshot `IERC20(token).balanceOf(address(this))` (or the dispatcher's balance, in the predispatch path) before and after each transfer/sweep, and credit `_orders[commitment][token]` with the measured delta (after protocol fee reduction) rather than the caller-declared `order.inputs[i].amount`/`reducedInputs[i].amount`. The commitment hash should also be computed over the corrected, actually-received amounts, exactly as done in `evm/src/apps/IntentGatewayV2.sol` lines 291–329, so that escrow accounting can never exceed the gateway's real token holdings.

## Proof of Concept
1. Deploy `evm/tron/contracts/apps/IntentGatewayV2.sol` and register a TRC-20 token implementing a 1% fee-on-transfer (analogous to the `FeeOnTransferToken` test helper already used in the EVM test suite [5](#0-4) ) as an input asset.
2. User calls `placeOrder` with `order.inputs[0].amount = 1000e18` of this token, no predispatch calldata.
3. `IERC20(token).safeTransferFrom(msg.sender, address(this), 1000e18)` executes, but due to the 1% fee, the gateway's actual balance increases by only `990e18`.
4. `_orders[commitment][token] += reducedInputs[0].amount` credits `1000e18` (minus any protocol fee) to the escrow ledger — a value strictly greater than what the gateway physically received (`990e18`).
5. A solver later fills the order and attempts to claim the full escrowed amount recorded in `_orders[commitment][token]`; the gateway's actual token balance for that token is insufficient to pay out all outstanding escrow claims once multiple orders using this token exist, demonstrating the freezing/undercollateralization impact — mirroring the Lido PoC where `previewDeposit` differs before/after `initiateETHWithdrawalsFromLido` due to the same "counter incremented by nominal amount, not actual balance moved" root cause.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L291-306)
```text
            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2440-2494)
```text
    /// @notice Escrow correctly reflects actual received amount for fee-on-transfer tokens.
    function testPlaceOrder_FeeOnTransferToken_EscrowMatchesReceived() public {
        // Deploy a 1% fee-on-transfer token
        FeeOnTransferToken fot = new FeeOnTransferToken(100); // 1% = 100 bps
        fot.mint(user, 10000 * 1e18);

        uint256 inputAmount = 1000 * 1e18;
        uint256 expectedReceived = inputAmount - (inputAmount * 100) / 10000; // 990

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(fot)))), amount: inputAmount});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 900 * 1e18});

        PaymentInfo memory output =
            PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: outputAssets, call: ""});

        Order memory order = Order({
            user: bytes32(0),
            source: "",
            destination: host.host(),
            deadline: block.number + 100,
            nonce: 0,
            fees: 0,
            session: address(0),
            predispatch: DispatchInfo({assets: new TokenInfo[](0), call: ""}),
            inputs: inputs,
            output: output
        });

        vm.startPrank(user);
        fot.approve(address(intentGateway), inputAmount);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();

        // Gateway should hold only what it actually received
        assertEq(
            fot.balanceOf(address(intentGateway)), expectedReceived, "Gateway balance should match received amount"
        );

        // Reconstruct the order as placeOrder would have mutated it
        order.user = bytes32(uint256(uint160(user)));
        order.source = host.host();
        order.nonce = 0;
        order.inputs[0].amount = expectedReceived;
        bytes32 commitment = keccak256(abi.encode(order));

        // Escrow should match actual received, not the user-specified amount
        assertEq(
            intentGateway._orders(commitment, address(fot)),
            expectedReceived,
            "Escrow should equal actual received amount"
        );
    }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2690-2735)
```text
contract FeeOnTransferToken {
    string public name = "FeeOnTransferToken";
    string public symbol = "FOT";
    uint8 public decimals = 18;
    uint256 public totalSupply;
    uint256 public feeBps;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    constructor(uint256 _feeBps) {
        feeBps = _feeBps;
    }

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
        totalSupply += amount;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        return _transfer(msg.sender, to, amount);
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        uint256 allowed = allowance[from][msg.sender];
        if (allowed != type(uint256).max) {
            allowance[from][msg.sender] = allowed - amount;
        }
        return _transfer(from, to, amount);
    }

    function _transfer(address from, address to, uint256 amount) internal returns (bool) {
        uint256 fee = (amount * feeBps) / 10_000;
        uint256 received = amount - fee;
        balanceOf[from] -= amount;
        balanceOf[to] += received;
        // fee is burned
        totalSupply -= fee;
        return true;
    }
}
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L416-446)
```text
            // Transfer tokens from call dispatcher back to IntentGateway
            Call[] memory transferCalls = new Call[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;
                uint256 balance;

                if (token == address(0)) {
                    balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }

                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-469)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
        }
```
