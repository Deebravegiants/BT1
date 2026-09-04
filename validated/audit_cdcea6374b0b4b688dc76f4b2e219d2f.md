### Title
`LifiExternalAction.swap`/`callRouter` blindly forward attacker-controlled router calldata against an unlimited allowance, letting an Emporium stateless op drain the action's held ERC20 balance and launder it into the attacker's own UTXO - ([File: contracts/external-actions/swaps/LifiExternalAction.sol], [File: contracts/external-actions/swaps/ExternalActionSwap.sol])

### Summary
`LifiExternalAction` and `EmporiumUpgradeable` both gate `runAction` with `onlyAllowedRecipient`, but that modifier only checks `msg.sender`, not the origin of the proof. Because `EmporiumUpgradeable.runAction`'s "Case 2: Stateless Interaction" branch performs a raw `op.endpoint.call(op.callData)` [1](#0-0) , an attacker who submits their own valid Hinkal proof for an Emporium-routed transaction can set `op.endpoint = LifiExternalAction` and `op.callData` to a forged `runAction(circomData2, deltaAmounts2)` call whose fields are never constrained by any circuit or by the outer `deltaAmountChanges`. Since `msg.sender` becomes `Emporium` (an allowed recipient of `LifiExternalAction`), `onlyAllowedRecipient` passes, and `swap()`/`callRouter()` then forward the attacker's arbitrary `externalActionMetadata` to `router` while `router` already holds `approveUnlimited` allowance over `LifiExternalAction`'s token balance from any prior legitimate swap.

### Finding Description
Broken equality: the amount of `inputToken` actually consumed from `LifiExternalAction`'s balance during `callRouter`'s `router.call(externalActionMetadata)` should equal `inputAmount = uint256(-deltaAmounts[0])`, a value that is supposed to be bound to a Groth16-verified `deltaAmountChanges` vector. In reality, `callRouter` never checks the input-token balance delta at all - it only measures `swappedAmount = getERC20OrETHBalance(outputToken) - balanceBefore` [2](#0-1) , and `inputAmount` is used only for `msg.value` sizing in the native-ETH branch, never for the ERC20 branch where the router pulls tokens via the pre-existing `approveUnlimited(inputToken, router)` allowance [3](#0-2) .

Exploit path:
1. Attacker deposits/holds their own funds and generates a valid proof for their own `transact()` call with `externalActionData.externalActionId` = Emporium's id.
2. Inside the proof-committed `circomData.externalActionData.externalActionMetadata`, the attacker encodes an `EmporiumStack` whose `ops[i]` is a **stateless** op (`invokeWallet = false`, no `signerAddress` gating that op) with `endpoint = LifiExternalAction` and `callData = abi.encodeCall(runAction, (forgedCircomData2, forgedDeltaAmounts2))`.
3. `Hinkal.transact` verifies the proof only over the *outer* `circomData` (tokens/`amountChanges`/nullifiers for the attacker's own account) [4](#0-3) ; the nested `forgedCircomData2`/`forgedDeltaAmounts2` bytes are opaque payload, never decoded or constrained by the circuit.
4. `EmporiumUpgradeable.runAction` executes the stateless call: `LifiExternalAction.runAction(forgedCircomData2, forgedDeltaAmounts2)` is invoked with `msg.sender == Emporium`. If Emporium is in `LifiExternalAction`'s `isAllowedRecipient` set, `onlyAllowedRecipient` passes [5](#0-4) .
5. `swap()` sizes `inputAmount` from the forged, unverified `deltaAmounts2[0]` [6](#0-5) , but the real amount pulled is whatever the attacker encoded into `forgedCircomData2.externalActionData.externalActionMetadata` sent to `router`, which can drain the *entire* residual/allowed ERC20 balance `LifiExternalAction` holds (accumulated dust from any prior legitimate user swap, since `approveUnlimited` never shrinks).
6. The resulting `outputToken` proceeds land on `Emporium` (as `msg.sender` in `swap()`'s final transfer) [7](#0-6) , are captured by Emporium's own `balancesAfter - balancesBefore` accounting [8](#0-7) , and forwarded to Hinkal as a legitimate-looking output UTXO for the attacker's own outer proof (`outTotal = inTotal + amountChanges`), laundering the stolen funds into the attacker's own account with full "proof coverage" at the outer layer even though the value's true origin was never authorized.

Existing guards fail because: `onlyAllowedRecipient` authenticates only the immediate caller address, not the provenance of the call; the Groth16 proof only constrains the outer `circomData`, never the bytes payload passed to a nested stateless Emporium op; and `callRouter` has no check tying the router's actual token consumption to the declared `deltaAmounts`.

### Impact Explanation
Critical - direct theft of ERC20 balances held by `LifiExternalAction` (residual dust and any allowance-reachable balance from prior swaps) is laundered into the attacker's own Hinkal UTXO, appearing as a normal deposit backed 1:1 by "found" funds that in fact belong to the protocol/other depositors' swap residue. This is repeatable every time `LifiExternalAction` accumulates a nonzero balance after a legitimate swap and requires only the precondition that Emporium is configured as an allowed recipient of `LifiExternalAction` (a plausible, likely-intended integration, since Emporium's purpose is to invoke external DeFi actions on the user's behalf).

### Likelihood Explanation
Preconditions: (1) Emporium listed in `LifiExternalAction.isAllowedRecipient` - a deployment/admin configuration decision not verifiable purely from this repo's constructors, but a natural integration setup given Emporium's design intent; (2) `LifiExternalAction` holds a nonzero residual ERC20 balance from any prior swap (dust is a stated/likely occurrence, since `swap()` only forwards `amountToSendToHinkal`, net of fees, and the router's actual consumption is unchecked). Attacker cost is a single valid self-proof plus crafting the nested calldata; no privileged role or victim key is required. The attack is repeatable each time dust/balance accrues on `LifiExternalAction`.

### Recommendation
- In `callRouter`/`swap`, verify the actual `inputToken` balance decrease equals the declared `inputAmount` (mirroring the `swappedAmount` check already done for the output token), reverting on mismatch.
- Do not rely on `onlyAllowedRecipient` (a same-address check) as the sole authorization gate when a caller (like Emporium) can be tricked into relaying arbitrary calldata to another allowed-recipient action; require the top-level circuit to constrain/hash any nested `externalActionMetadata` routed through Emporium's stateless ops before they reach other external actions, or disallow stateless Emporium ops from targeting other `ExternalActionBase`-derived `runAction` entry points entirely.
- Replace `approveUnlimited` with a per-call approval scoped exactly to the verified `inputAmount`, reset after use.

### Proof of Concept
Foundry fork test plan:
1. Deploy `LifiExternalAction` with `router` mocked, and `Emporium` (or a mock allowed-recipient contract) added to `isAllowedRecipient`.
2. Seed `LifiExternalAction` with a residual ERC20 balance (e.g., 1000 USDC) representing prior-swap dust, and let `router` already hold unlimited allowance from a prior legitimate `swap()` call.
3. Craft an `EmporiumStack` with a stateless op: `endpoint = LifiExternalAction`, `callData = abi.encodeCall(runAction, (forgedCircomData2, forgedDeltaAmounts2))` where `forgedCircomData2.externalActionData.externalActionMetadata` instructs the mock router to `transferFrom(LifiExternalAction, attacker, 1000e6)` on USDC and mint/transfer some `outputToken` back to `LifiExternalAction` to satisfy `swappedAmount`.
4. Generate a real proof for the attacker's own minimal outer deposit/transact through `Hinkal.transact`, embedding the Emporium stack above.
5. Assert: (a) `LifiExternalAction`'s USDC balance drops by 1000 USDC beyond what `forgedDeltaAmounts2[0]` declared; (b) attacker's Hinkal UTXO set gains the equivalent value; (c) no Groth16 verification event ever covered `forgedCircomData2`/`forgedDeltaAmounts2`, confirming the theft occurred outside all proof constraints.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L102-113)
```text
            // CASE 2: Stateless Interaction
            else {
                bytes4 selector = bytes4(op.callData);
                if (
                    selector == IHinkalWallet.callHinkalWallet.selector ||
                    selector == IHinkalWallet.doSendToRelay.selector
                ) {
                    revert UnauthorizedWalletCall();
                }

                (success, err) = op.endpoint.call{value: op.value}(op.callData);
            }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-151)
```text
        uint256[] memory balancesAfter = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        UTXO[] memory utxoSet = new UTXO[](
            circomData.erc20TokenAddresses.length
        );

        uint256 utxoSetLength;

        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            int256 balanceChange = int256(balancesAfter[i]) -
                int256(balancesBefore[i]);

            if (deltaAmountChanges[i] < 0) {
                balanceChange -= deltaAmountChanges[i];
                // this equation reads: total change of emporium balance = what was moved to emporium (-deltaAmountChange) + how emporium balance changed through tx (balanceChange)
            }

            // the only case when balanceChange can be < 0, when there were some funds on emporium before the call
            if (balanceChange < 0) {
                revert BalanceChangeShouldBePositive();
            }

            UTXO memory utxoOut = handleOut(balanceChange, circomData, i);

            if (utxoOut.amount > 0) {
                utxoSet[utxoSetLength++] = utxoOut;
            }
        }
```

**File:** contracts/external-actions/swaps/LifiExternalAction.sol (L16-36)
```text
    function callRouter(
        address inputToken,
        uint256 inputAmount,
        address outputToken,
        bytes calldata externalActionMetadata
    ) internal override returns (uint256 swappedAmount) {
        uint256 balanceBefore = getERC20OrETHBalance(outputToken);

        if (inputToken == address(0)) {
            (bool success, ) = router.call{value: inputAmount}(
                externalActionMetadata
            );
            require(success, "LI.FI swap failed: native coin");
        } else {
            approveUnlimited(inputToken, router);
            (bool success, ) = router.call(externalActionMetadata);
            require(success, "LI.FI swap failed: erc-20 token");
        }

        swappedAmount = getERC20OrETHBalance(outputToken) - balanceBefore;
    }
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L29-35)
```text
    }

    receive() external payable {}

    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmounts
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L40-46)
```text
    function swap(
        CircomData calldata circomData,
        int256[] calldata deltaAmounts
    ) internal returns (UTXO[] memory utxoSet) {
        address inputToken = circomData.erc20TokenAddresses[0];
        uint256 inputAmount = uint256(-deltaAmounts[0]);

```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L91-93)
```text
        uint256 amountToSendToHinkal = swappedAmount - totalFee;

        transferERC20TokenOrETH(outputToken, msg.sender, amountToSendToHinkal);
```

**File:** contracts/Hinkal.sol (L37-65)
```text
        {
            uint256[] memory inputForCircom = hinkalHelper.performHinkalChecks(
                circomData,
                dimensions,
                msg.sender
            );

            require(
                verifyProof(
                    a,
                    b,
                    c,
                    inputForCircom,
                    buildVerifierId(
                        dimensions,
                        circomData.externalActionData.externalActionId
                    )
                ),
                "Invalid Proof"
            );
            // Root Hash Validation
            require(
                rootHashExists(
                    circomData.rootHashHinkal,
                    circomData.rootHashHinkalIndex
                ),
                "Hinkal Root Hash is Incorrect"
            );
        }
```

**File:** contracts/external-actions/ExternalActionBaseV2.sol (L16-22)
```text
    modifier onlyAllowedRecipient() {
        require(
            isAllowedRecipient[msg.sender],
            "ExternalActionBase: sender not allowed"
        );
        _;
    }
```
