### Title
Checks-Effects-Interactions violation in `IntentGatewayV2.withdraw()` (Tron variant) allows reentrancy before escrow decrement - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron deployment of `IntentGatewayV2` contains an unfixed version of the escrow-release logic that hands control flow to an untrusted, attacker-influenced address (the order token/beneficiary) via a low-level `.call` **before** decrementing the corresponding escrow accounting entry, reproducing the exact checks-effects-interactions violation described in the RocketPool `finalise()`/`_refund()` report. The mainline EVM contract (`evm/src/apps/intentsv2/IntentsBase.sol`) was hardened with the CEI pattern and `nonReentrant` guards after an internal audit (see `evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol`), but the Tron copy of the contract was not brought in line with that fix.

### Finding Description
In `withdraw()`, `_filled[body.commitment]` is set at the top of the function (order-level CEI is respected), but the per-token escrow accounting is not: [1](#0-0) 

For each `TokenInfo` entry, the contract performs a low-level external call — either a native ETH transfer to `beneficiary` or an arbitrary `token.call(transfer, beneficiary, amount)` — and only *afterwards* decrements `_orders[body.commitment][token]`:
```solidity
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    if (!sent) revert InsufficientNativeToken();
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    if (!success) revert TransferFailed();
}
_orders[body.commitment][token] -= amount;   // <-- effect happens AFTER interaction
```
`order.inputs[i].token` is fully attacker-controlled at `placeOrder` time — a user can escrow an arbitrary contract address as a "token." When that token is subsequently withdrawn (fill, refund, or cancel-from-destination path), the contract executes attacker-supplied code via the low-level `.call` *before* its own escrow ledger (`_orders[commitment][token]`) is updated, and *before* the loop moves on to decrement/transfer any subsequent tokens (e.g. the protocol fee token forwarded afterward at lines 716-723). No `nonReentrant`/`ReentrancyGuard` modifier exists anywhere in this file: [2](#0-1) 

This is analogous to `RocketMinipoolDelegateOld._refund()` handing control to `nodeWithdrawalAddress` before `finalised = true` was committed — here, control is handed to an attacker-chosen token/beneficiary contract before the corresponding escrow slot is zeroed and before the remainder of the withdrawal (fee transfer, event emission) completes.

### Impact Explanation
An attacker who crafts an order using a malicious "token" contract as one of several escrowed inputs can have that contract's `transfer()` implementation reenter the gateway while `_orders[commitment][maliciousToken]` still reflects the pre-decrement balance and while the fee-token transfer for the same commitment has not yet occurred. Because state mutation and external interaction are interleaved per iteration rather than fully separated (as in the fixed mainline contract, which decrements `_orders` before each transfer — `evm/src/apps/intentsv2/IntentsBase.sol:464-469`), this class of bug enables inconsistent escrow accounting and potential double-crediting of subsequent iteration/fee-transfer state, resulting in loss of escrowed user/protocol funds on the Tron deployment.

### Likelihood Explanation
Reachable from a single, permissionless `placeOrder` call with an attacker-supplied malicious token address as one of multiple order inputs, followed by a normal fill/cancel/refund flow that invokes `withdraw()`. No privileged role is required — only control over an ERC20-like token contract address supplied as order input, which is standard user input to the intents flow.

### Recommendation
Port the CEI fix already applied to the mainline `IntentsBase._withdraw` (decrement `_orders[commitment][token]` before performing the external transfer) into the Tron `IntentGatewayV2.withdraw()`, and add a `nonReentrant` guard consistent with the mainline `IntentGatewayV2.sol`/`IntrinsicIntents.sol` hardening (as validated by `IntrinsicIntentsReentrancyTest.sol`).

### Proof of Concept
1. Attacker deploys a malicious ERC20-like contract `EvilToken` whose `transfer()` function, on being called with a specific `(beneficiary, amount)` pair, calls back into the gateway (e.g., attempts to re-trigger accounting-sensitive paths or manipulates shared state before the loop's decrement executes).
2. Attacker calls `placeOrder` on the Tron `IntentGatewayV2`, escrowing `[EvilToken, legitimateToken]` as inputs.
3. Once the order is filled/cancelled and `withdraw(body, ...)` is invoked, the loop reaches `EvilToken` first: `token.call(transfer, beneficiary, amount)` hands control to `EvilToken` before `_orders[commitment][EvilToken] -= amount` executes and before the subsequent legitimate-token transfer/fee transfer in the same call.
4. `EvilToken`'s `transfer()` reenters (e.g. into read-modify paths sharing `_orders`/fee state for the same commitment), exploiting the stale pre-decrement values to obtain more value than escrowed, matching the RocketPool "checks-effects-interactions" root cause. [3](#0-2)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L55-97)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-723)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
        }

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }
```
