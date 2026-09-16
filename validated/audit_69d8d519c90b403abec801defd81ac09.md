### Title
CallDispatcher permanently locks any ETH sent to it since it has no withdraw/sweep function - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher` implements a bare `receive() external payable {}` to accept native ETH, but unlike every other Hyperbridge contract that accepts ETH (`EvmHost`, `IntentGatewayV2`, `WrappedHyperFungibleToken`, `SimplexPaymaster`), it provides **no** admin/owner withdraw or dust-sweep function to recover that ETH.

### Finding Description
`CallDispatcher.sol` declares:
```solidity
receive() external payable {}
``` [1](#0-0) 

and its only other function, `dispatch`, only forwards `call.value` amounts that a caller specifies in the `Call[]` array to arbitrary target contracts using the ETH already resident in `CallDispatcher`'s own balance:
```solidity
function dispatch(bytes memory encoded) external {
    Call[] memory calls = abi.decode(encoded, (Call[]));
    ...
    (bool success, bytes memory result) = to.call{value: call.value}(call.data);
    if (!success) revert CallFailed(to, result);
}
``` [2](#0-1) 

There is no `withdraw`, `sweep`, `sweepDust`, or `onlyOwner` recovery mechanism anywhere in the contract, and `dispatch` is `external` and unauthenticated for arbitrary callers (any address may call it and specify arbitrary `to`/`data`/`value`). Compare this to `EvmHost`, which explicitly documents its `receive()` as being for dust collection from a router and has dedicated `withdraw`/`sweep` logic elsewhere in the same contract [3](#0-2) , and to `IntentGatewayV2`, which emits `DustCollected`/`DustSwept` events and has dust-sweeping functionality tied to its `receive()` [4](#0-3) , and to `WrappedHyperFungibleToken`, whose `receive()` is only meant to catch native ETH mid-flow from `IWETH.withdraw()` inside `onPostRequestTimeout` before it is immediately forwarded to a `refundee` [5](#0-4) .

`CallDispatcher` is used by the intents subsystem (`evm/src/apps/intentsv2/IntentsBase.sol`) to execute post-fill/solver calls with attached native value taken from the contract's own balance. Since `CallDispatcher` has no way to track or reconcile "excess" ETH beyond what a specific `dispatch()` invocation consumes, any ETH sent to the contract — whether by user error (misdirected transfer), a solver overfunding the contract ahead of a `dispatch()` call, or leftover value after a partial/failed batch of calls — becomes permanently unrecoverable. There is no owner, no `Ownable`, and no privileged function anywhere in this contract that can move ETH back out except via the generic `dispatch()` path (which requires the caller to specify a target contract and any value they want forwarded from the balance — this can drain it, but cannot be used by the original depositor to reliably recover funds if others race to call `dispatch()` first, and provides no dedicated recovery guarantee).

### Impact Explanation
Any native ETH that ends up in `CallDispatcher`'s balance without being immediately consumed by a `dispatch()` call is permanently frozen — no function exists to return it to depositors or sweep it to a treasury/beneficiary. This constitutes a permanent freezing-of-funds condition reachable by any ordinary user or by the intents system's normal operation whenever `CallDispatcher` accumulates unspent value (e.g., through overestimated `call.value` amounts, direct mis-sent transfers, or partial batch failures reverting mid-array before consuming later ETH).

### Likelihood Explanation
Likelihood is moderate: the contract is a general-purpose, permissionless call-dispatch utility used in the intents flow (`IntentsBase.sol`), and its `receive()` function accepts ETH from anyone with no restriction, making it trivial for a user or integrator to accidentally (or a malicious solver to deliberately) leave stray ETH in the contract.

### Recommendation
Add a privileged (or at minimum, depositor-tracked) rescue/sweep function to `CallDispatcher` to recover ETH balance not consumed by `dispatch()`, or restrict `receive()` to reject unsolicited transfers (revert unless called in the context of an active `dispatch()`), mirroring the dust-sweep patterns already used in `EvmHost` and `IntentGatewayV2`.

### Proof of Concept
1. Any external account or contract sends native ETH directly to `CallDispatcher` via a plain transfer, triggering `receive() external payable {}` [1](#0-0) .
2. The ETH is now part of `CallDispatcher`'s balance with no bookkeeping tying it to the sender.
3. Since `dispatch()` is the only function capable of moving ETH out, and it requires an unrelated caller to supply a `Call[]` targeting a chosen `to`/`value`/`data` [2](#0-1) , the original sender has no guaranteed mechanism to reclaim their funds — the ETH is permanently locked unless a third party happens to route a `dispatch()` call that sends it back out (which is not guaranteed, and could just as easily be swept by an unrelated actor's `dispatch()` call to their own target).

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L36-39)
```text
    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}
```

**File:** evm/src/utils/CallDispatcher.sol (L44-61)
```text
    function dispatch(bytes memory encoded) external {
        Call[] memory calls = abi.decode(encoded, (Call[]));
        uint256 callsLen = calls.length;
        for (uint256 i = 0; i < callsLen; ++i) {
            Call memory call = calls[i];
            uint32 size;
            address to = call.to;
            assembly {
                size := extcodesize(to)
            }

            if (size == 0) {
                revert NotContract(to);
            }

            (bool success, bytes memory result) = to.call{value: call.value}(call.data);
            if (!success) revert CallFailed(to, result);
        }
```

**File:** evm/src/core/EvmHost.sol (L383-386)
```text
    /*
     * @dev receive function for UniswapV2Router02, collects all dust native tokens.
     */
    receive() external payable {}
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L235-266)
```text
    /**
     * @dev Emitted when some dust tokens are accrued.
     * @param token The token contract address of the dust, address(0) for native currency.
     * @param amount The amount of dust collected.
     */
    event DustCollected(address token, uint256 amount);

    /**
     * @dev Emitted when some dust tokens are swept.
     * @param token The token contract address of the fee, address(0) for native currency.
     * @param amount The amount of dust to be swept.
     * @param beneficiary The beneficiary of the funds
     */
    event DustSwept(address token, uint256 amount, address beneficiary);

    /**
     * @dev Emitted when a destination-specific protocol fee is updated.
     * @param stateMachineId The hashed state machine identifier of the destination chain.
     * @param feeBps The protocol fee in basis points for this destination.
     */
    event DestinationProtocolFeeUpdated(bytes32 indexed stateMachineId, uint256 feeBps);

    constructor(address admin) EIP712("IntentGateway", "2") {
        _admin = admin;
    }

    /**
     * @notice Fallback function to receive ether
     * @dev This function is called when ether is sent to the contract without data
     * @custom:note The function is marked payable to allow receiving ether
     */
    receive() external payable {}
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L344-368)
```text
    function onPostRequestTimeout(PostRequestTimeout calldata incoming) external override onlyHost whenNotPaused {
        HyperFungibleToken.Message memory message = abi.decode(incoming.request.body, (HyperFungibleToken.Message));
        address refundee = _toAddr(message.from);

        if (_isWeth) {
            // Try a native-ETH push first; if the refundee cannot accept native value
            // (e.g. the caller used the ERC-20 deposit path in `send()` from a
            // non-payable contract), re-wrap the withdrawn ETH and deliver the
            // underlying WETH as an ERC-20 transfer so the timeout still settles and
            // funds are not permanently locked.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = refundee.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(refundee, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(refundee, message.amount);
        }

        emit Refunded({to: refundee, amount: message.amount});
    }

    /// @notice Accepts native ETH transfers, required for receiving ETH from WETH.withdraw()
    receive() external payable {}
```
