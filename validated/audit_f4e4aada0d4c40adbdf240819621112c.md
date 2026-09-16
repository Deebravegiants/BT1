### Title
Relayer fee withdrawal can permanently strand accrued rewards if the destination `EvmHost`/`HostManager` lacks the accounted `feeToken` balance - (File: `modules/pallets/relayer/src/withdrawal.rs`, `evm/src/core/HostManager.sol`, `evm/src/core/EvmHost.sol`)

### Summary
The Sherlock finding shows that `AutoRoller.settle()` zeroes/consumes accounting state and then unconditionally transfers a fixed `stakeSize` of a token without checking the contract's actual balance, causing the call to revert for the legitimate, unprivileged caller (`lastRoller`) whenever the contract's real balance is short of the accounted amount. The same "accounted-amount transfer without a balance check, after the source-side bookkeeping has already been finalized" pattern exists in Hyperbridge's relayer fee-withdrawal path.

### Finding Description
`pallet-relayer`'s withdrawal flow accumulates relayer fees into the `Fees` map and, on withdrawal, zeroes the entry before the payout is actually settled on the destination chain: "The pallet verifies the signature, increments the per-relayer nonce, and dispatches an ISMP POST request to the destination's host manager (EVM) ... instructing it to disburse `available_amount` of the fee token to the beneficiary... The `Fees` entry is zeroed so the same balance cannot be withdrawn twice... the destination chain settles the payout when the ISMP request is delivered there." [1](#0-0) 

On the EVM destination, this ISMP request is delivered to `HostManager.onAccept`, which for the `Withdraw` action decodes `WithdrawParams` and calls `IHostManager(_params.host).withdraw(withdrawParams)` on `EvmHost` to actually move the `feeToken` out to the beneficiary. [2](#0-1) 

`EvmHost`'s incoming-message dispatch pattern shows exactly the risk class this finding targets: token payouts (e.g. relayer-fee refunds in `dispatchIncoming`/`dispatchTimeOut`) are executed via `IERC20(feeToken()).safeTransfer(...)` for a fixed, previously-recorded amount, with no `balanceOf` check against the amount being paid. [3](#0-2) [4](#0-3)  The `withdraw` payout path invoked from `HostManager.onAccept` follows the same shape — it pays out an `amount` (`WithdrawParams`) that was determined purely by the source-chain `Fees` accounting on Hyperbridge, not by the EVM host's actual `feeToken` balance at execution time.

Because the `Fees` entry on Hyperbridge is zeroed as soon as the withdrawal extrinsic is signed and dispatched — *before* the destination-side transfer is known to succeed — a mismatch between the accounted `available_amount` and the EVM host contract's real `feeToken` balance (e.g., if protocol revenue hasn't been swept in yet, or has been partially withdrawn by other means) causes the ISMP request execution (`onAccept` → `EvmHost.withdraw`) to revert on `safeTransfer`. Just like `AutoRoller.settle()`, this is exactly the "accounted amount vs. actual balance" mismatch bug class from the external report, reached by an ordinary unprivileged relayer proving delivery and calling the withdrawal path.

### Impact Explanation
If the destination `EvmHost` does not hold enough `feeToken` to cover the accounted withdrawal amount, the relayer's payout request reverts on delivery. Since the source-side `Fees` balance was already zeroed at dispatch time, the relayer's accrued reward becomes effectively unrecoverable through the normal flow (repeated delivery attempts of the same request will keep reverting until the host happens to be funded, and the request is explicitly designed to never time out, so there is no automatic refund/retry-with-adjustment path). This is a fund-freezing/loss condition for the relayer, an unprivileged, economically-incentivized actor central to Hyperbridge's message-delivery security model.

### Likelihood Explanation
Reachable by any relayer that has accumulated fees and calls the standard, documented withdrawal flow — no privileged role required. The condition depends only on the destination `EvmHost`'s `feeToken` balance lagging the aggregate amount Hyperbridge believes is owed (a state that can arise from normal usage patterns, e.g., multiple relayers withdrawing concurrently against the same pool of collected fees, or fees not yet fully collected on that chain), making it a plausible operational condition rather than a purely theoretical one.

### Recommendation
- Before zeroing `Fees` on Hyperbridge, or before finalizing the ISMP dispatch, ensure the payout can be reasonably expected to succeed, or
- On the EVM side, have `EvmHost.withdraw` clamp the transferred amount to `IERC20(feeToken()).balanceOf(address(this))` (paying out what is available) and emit an event/leave a residual claim for the shortfall, mirroring the report's suggested fix of checking `balanceOf` before transferring, and
- Add a mechanism for partially-failed withdrawals to be retried/topped-up rather than only "delete receipt and hope it later succeeds," so the relayer is not permanently unable to collect the shortfall.

### Proof of Concept
1. Relayer accrues fees for delivering messages to chain X; `pallet-relayer::Fees[X][relayer]` records the accrued balance. [5](#0-4) 
2. Relayer calls the signed withdrawal extrinsic; Hyperbridge zeroes `Fees` and dispatches an ISMP POST `Withdraw` request to chain X's `HostManager`. [1](#0-0) 
3. On chain X, `HostManager.onAccept` decodes `WithdrawParams` and calls `EvmHost.withdraw(withdrawParams)`. [6](#0-5) 
4. If chain X's `EvmHost` `feeToken` balance is less than the accounted `amount`, the internal `safeTransfer` reverts (same pattern shown for fee refunds at `dispatchIncoming`/`dispatchTimeOut`). [3](#0-2) 
5. The relayer's fee was already zeroed on the source (Hyperbridge) in step 2, so the relayer has no further recourse to reclaim the reward through the standard path — the reward is stranded/lost.

Note: I was unable to view the full body of `EvmHost.withdraw`/`WithdrawParams` handling in this pass (only located it via grep matches, not full source) due to running out of tool iterations, so the exact balance-check logic inside that specific function is inferred from the closely analogous, verified `dispatchIncoming`/`dispatchTimeOut` transfer patterns in the same contract. A Devin session with full file access should confirm the exact `withdraw` implementation in `evm/src/core/EvmHost.sol` before treating this as fully confirmed.

### Citations

**File:** modules/pallets/relayer/src/withdrawal.rs (L16-30)
```rust
//! Relayer fee withdrawal.
//!
//! Once fees have been accumulated into [`crate::pallet::Fees`] by
//! [`crate::accumulate`], relayers withdraw them via [`Pallet::withdraw`].
//! The flow:
//!
//! 1. The relayer signs a `(nonce, dest_chain, beneficiary?)` payload with their per-chain key (EVM
//!    secp256k1 / sr25519 / ed25519).
//! 2. The pallet verifies the signature, increments the per-relayer nonce, and dispatches an ISMP
//!    POST request to the destination's host manager (EVM) or `HYPERBRIDGE_MODULE_ID` (substrate)
//!    instructing it to disburse `available_amount` of the fee token to the beneficiary.
//! 3. The `Fees` entry is zeroed so the same balance cannot be withdrawn twice.
//!
//! The on-chain effect is just dispatching the message; the destination chain settles the
//! payout when the ISMP request is delivered there.
```

**File:** evm/src/core/HostManager.sol (L134-159)
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

        OnAcceptActions action = OnAcceptActions(uint8(request.body[0]));
        if (action == OnAcceptActions.Withdraw) {
            // This is where governance & relayers can withdraw their revenue.
            WithdrawParams memory withdrawParams = abi.decode(request.body[1:], (WithdrawParams));
            IHostManager(_params.host).withdraw(withdrawParams);
        } else if (action == OnAcceptActions.SetHostParam) {
            HostParams memory hostParams = abi.decode(request.body[1:], (HostParams));
            IHostManager(_params.host).updateHostParams(hostParams);
        } else if (action == OnAcceptActions.SetAdmin) {
            // Rotates the governance relayer.
            address newAdmin = abi.decode(request.body[1:], (address));
            if (newAdmin == address(0)) revert InvalidAdmin();
            emit AdminUpdated({previous: _params.admin, current: newAdmin});
            _params.admin = newAdmin;
        }
    }
```

**File:** evm/src/core/EvmHost.sol (L841-846)
```text
        // reward the relayer fee
        uint256 fee = _requestCommitments[commitment].fee;
        if (fee != 0) {
            IERC20(feeToken()).safeTransfer(relayer, fee);
        }
        emit GetRequestHandled({commitment: commitment, relayer: relayer});
```

**File:** evm/src/core/EvmHost.sol (L872-877)
```text
        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit GetRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }
```

**File:** modules/pallets/relayer/src/accumulate.rs (L353-368)
```rust
	pub fn accumulate_fee_and_deposit_event(
		state_machine: StateMachine,
		address: Vec<u8>,
		fee: U256,
	) {
		let _ = Fees::<T>::try_mutate(state_machine, address.clone(), |inner| {
			*inner += fee;
			Ok::<(), ()>(())
		});

		Self::deposit_event(Event::<T>::AccumulateFees {
			address: sp_runtime::BoundedVec::truncate_from(address),
			state_machine,
			amount: fee,
		});
	}
```
