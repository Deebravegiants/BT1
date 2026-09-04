### Title
Emporium `runAction` skips ALL balance accounting when `erc20TokenAddresses.length == 0`, letting an unsigned op drain any funds Emporium holds - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
When `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `formInputForCircom` routes to `formInputEmporiumMin`, which only proves knowledge of a `messageSeed` (`message == Poseidon(messageSeed)`) with no constraint on the `EmporiumStack` ops. Combined with `EmporiumUpgradeable.runAction`'s balance-diff loop operating over the (now empty) `erc20TokenAddresses` array and `verifyWallet` short-circuiting signature checks when `stack.signerAddress == address(0)`, an attacker can force Emporium to execute an arbitrary `.call` as itself with zero accounting and zero authorization.

### Finding Description
The claimed invariant "assets Emporium can move in a tx == assets accounted in balancesBefore/balancesAfter" is broken.

Reachable path:
1. `contracts/CircomDataBuilder.sol:134-148` (`formInputForCircom`): if `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0`, only `formInputEmporiumMin` (lines 150-161) is used, which produces just `[emporiumMessage, timeStamp, calldataHash]` — no `stealthAddressStructure`, no `amountChanges`, no `erc20TokenAddresses`, and critically **no constraint at all on `externalActionData.externalActionMetadata`** (the encoded `EmporiumStack`).
2. `contracts/HinkalHelper.sol:64-171` (`dimensionsCheck`) only requires `erc20TokenAddresses.length == dimensions.tokenNumber`; `tokenNumber == 0` is not forbidden.
3. `contracts/Hinkal.sol:82-86` builds `oldBalances`/`newBalances` over the empty `erc20TokenAddresses`, so Hinkal itself tracks nothing either.
4. `_externalTransact` (`contracts/Hinkal.sol:234-261`) builds `deltaAmountChanges` of length 0 and calls `EmporiumUpgradeable.runAction`.
5. In `EmporiumUpgradeable.runAction` (`contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:76-160`):
   - `balancesBefore = getBalancesForArray(circomData.erc20TokenAddresses)` → `[]`.
   - `verifyWallet` (lines 302-349): when `stack.signerAddress == address(0)` it returns immediately at line 314-316, **skipping the EIP-712 signature check entirely** — the ops are never authorized by anyone.
   - The ops loop (lines 91-118) executes `op.endpoint.call{value: op.value}(op.callData)` as Emporium itself (only `callHinkalWallet`/`doSendToRelay` selectors are blocked).
   - `balancesAfter` is computed over the same empty array, so the loop at lines 132-151 that would normally revert on unaccounted balance loss (`BalanceChangeShouldBePositive`) never executes.

Because `erc20TokenAddresses` is fully attacker-controlled and unrelated to what `stack.ops` actually touches, the attacker sets it to `[]` to disable the only safety net (the balance-diff check), while `signerAddress = address(0)` disables the only authorization check (the EIP-712 signature). The op can then call any ERC20 (or other contract) Emporium has authority over — e.g. `token.transfer(attacker, emporiumBalance)` moving Emporium's own resting/in-flight balance, or `token.transferFrom(victim, attacker, amount)` consuming any standing allowance a victim granted to the Emporium address — with `msg.sender == Emporium` and no accounting or signature ever checked.

`performHinkalChecks`, `dimensionsCheck`, `checkOnchainCreation`, `rootHashExists`, and `verifyProof` do not prevent this: they validate the *shape* of `circomData` and a trivial Poseidon preimage, but never constrain the contents of `externalActionMetadata`/`stack.ops`, and `getHashedCalldata`/`calldataHash` only guarantee the attacker's own submitted calldata is self-consistent — not that it is safe.

### Impact Explanation
Any token balance or ETH resting in the Emporium contract at call time — whether from another user's in-flight multi-leg Emporium operation landing earlier in the same block, dust/rounding, or a standing ERC20 approval granted to Emporium by any party — can be transferred out to the attacker with a single crafted `Hinkal.transact` call using a trivial Min-circuit proof. This is direct theft of shielded/in-flight user funds and is repeatable every time Emporium holds any balance, matching the Critical severity category.

### Likelihood Explanation
Preconditions are minimal and fully within an unprivileged attacker's control: craft `circomData` with `erc20TokenAddresses = []`, `dimensions.tokenNumber = 0`, `externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `feeStructure.flatFee = 0` (to skip the `payRelayFees` revert path), and an `externalActionMetadata` encoding `EmporiumStack{signerAddress: address(0), ops: [...]}`. Generating a valid proof for `MainEVMCircuitMin` only requires knowledge of any `messageSeed`, which the attacker freely picks. Cost is a single transaction's gas plus proof generation; theft is bounded only by whatever balance Emporium happens to hold, and can be repeated whenever such a balance exists (including opportunistically racing/ordering within a block against other users' Emporium flows).

### Recommendation
- In `EmporiumUpgradeable.runAction`, do not allow `signerAddress == address(0)` to bypass authorization for arbitrary `op.endpoint.call` execution; require either a valid signature over the ops or restrict unsigned/"stateless" ops to a strictly allow-listed set of endpoints/selectors.
- Do not permit the Emporium external action to be invoked with `erc20TokenAddresses.length == 0` (reject the Min-circuit path for `HINKAL_EMPORIUM_ACTION_ID`, or require at least one token be tracked), or otherwise ensure balance accounting cannot be trivially disabled by supplying an empty token list.
- Bind `stack.ops` (or a hash of it) into the circuit's public inputs/constraints so the metadata cannot diverge from what the balance-diff logic is prepared to account for.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (as allowed recipient), register the Min verifier (`VerifierEVMMin0v4`) for `buildVerifierId({tokenNumber:0,nullifierAmount:0,outputAmount:0}, HINKAL_EMPORIUM_ACTION_ID)`.
2. Fund the Emporium contract directly with an ERC20 token (simulating in-flight/resting balance), e.g. `token.mint(emporium, 100e18)`.
3. Construct `circomData`: `erc20TokenAddresses = []`, `dimensions = {0,0,0}`, `externalActionData = {externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalAddress: emporium, externalActionMetadata: abi.encode(EmporiumStack{signerAddress: address(0), ops: [EmporiumOperation{endpoint: token, invokeWallet: false, value: 0, callData: abi.encodeCall(token.transfer, (attacker, 100e18))}], maxFee:0, deadline: type(uint256).max})}`, `feeStructure.flatFee = 0`, valid `rootHashHinkal`/index, nonzero `stealthAddressStructure.H0x`.
4. Generate a genuine snarkJS proof for `MainEVMCircuitMin` with an arbitrary `messageSeed`, computing `emporiumMessage`, `timeStamp`, `calldataHash` consistent with `getHashedCalldata`.
5. Call `Hinkal.transact(a,b,c,dimensions,circomData)` from an attacker EOA.
6. Assert: `token.balanceOf(attacker) == 100e18` and `token.balanceOf(emporium) == 0` after the call, i.e. Emporium's balance == 0 (before) vs stolen (after) while `balancesBefore == balancesAfter == []` inside `runAction`, proving the accounting invariant never fired.