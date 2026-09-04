### Title
Uncapped router approval lets an attacker's swap pull stranded/residual token balance out of `ExternalActionSwap` into their own output UTXO - (File: `contracts/external-actions/swaps/ExternalActionSwap.sol`, `contracts/external-actions/swaps/LifiExternalAction.sol`)

### Summary
`ExternalActionSwap.swap` computes `inputAmount` from `-deltaAmounts[0]` but never enforces that the router actually consumes only that amount. `LifiExternalAction.callRouter` grants the router unlimited (`approveUnlimited`) allowance over `inputToken` and then executes an attacker-supplied `externalActionMetadata` blob verbatim, so the amount actually pulled from the contract is fully attacker-controlled and decoupled from `inputAmount`. Any token balance already sitting in the shared action contract - e.g. relay fees stranded there because a prior transaction set `circomData.relay == address(0)` (so `sendToRelay` no-ops while the fee was already withheld/deducted from `amountToSendToHinkal`), or excess left behind by a fee-on-transfer token shortfall - can therefore be swept into the swap and credited entirely to the attacker's own output UTXO.

### Finding Description
The invariant that should hold is: *tokens leaving `ExternalActionSwap` in a transaction == -deltaAmountChanges that Hinkal sent it that transaction*. This is broken because the actual amount consumed by the LI.FI router is not bound to `inputAmount`.

In `swap()`: [1](#0-0) 
`inputAmount` is derived from `-deltaAmounts[0]` (minus flat fee if the input token is the fee token) and passed into `callRouter`, but in `LifiExternalAction.callRouter`: [2](#0-1) 
for the ERC-20 path, `inputAmount` is never used to bound the transfer - the contract calls `approveUnlimited(inputToken, router)` (unlimited allowance) and then executes `router.call(externalActionMetadata)`, where `externalActionMetadata` is attacker-supplied calldata forwarded from `circomData.externalActionData.externalActionMetadata`. The router can therefore pull any amount of `inputToken` up to the contract's full balance, not just the caller's own `inputAmount`.

`swappedAmount` is then simply the balance delta of `outputToken` around that call:
```
swappedAmount = getERC20OrETHBalance(outputToken) - balanceBefore;
```
This measurement faithfully captures whatever the router delivered - including output generated from any *extra* input consumed beyond the caller's own `inputAmount`. Back in `swap()`, that entire `swappedAmount` (minus fees) becomes `amountToSendToHinkal`, which is transferred to `msg.sender` (Hinkal) and packaged into a UTXO for the attacker's `stealthAddressStructure`.

Root cause of the "stranded" balance: when `circomData.relay == address(0)`, `sendToRelay` is a no-op: [3](#0-2) 
but the fee amounts (`relayFee`, `hinkalFee`) are still subtracted from `amountToSendToHinkal` / withheld from `inputAmount` in `swap()`, so those tokens are never sent anywhere and remain parked in the shared action contract as a residual balance available to the *next* caller.

Hinkal's own consistency check cannot catch the theft: [4](#0-3) 
This equation only verifies that Hinkal's balance delta matches the caller's own declared `amountChanges[i]` plus the UTXO amount created by the action - both of which are controlled by the attacker (their own proof, and the action's own output construction from `swappedAmount`). It never checks that the swap's input consumption equals `-deltaAmountChanges` sent to the action, so a swap that quietly grabs extra residual `inputToken` and turns it into extra `outputToken` passes the check trivially.

### Impact Explanation
An attacker who calls `Hinkal.transact` for a LI.FI swap can craft `externalActionMetadata` so the router pulls more `inputToken` than the amount Hinkal actually sent them for that transaction, consuming any stranded balance left in the shared `LifiExternalAction`/`ExternalActionSwap` contract (e.g., fees stranded from a prior `relay == address(0)` transaction, or residue from any other source such as fee-on-transfer shortfalls). The extra swap output is credited in full to the attacker's own UTXO. This is direct theft of protocol/relay fee balances or in-flight funds parked in the action contract, matching Critical/High severity (direct theft of shielded/in-flight funds, or theft of protocol/relay fees), and is repeatable every time a residual balance accumulates.

### Likelihood Explanation
Preconditions: (1) some non-zero balance of a token must already sit in the shared `ExternalActionSwap`/`LifiExternalAction` contract (plausible via the `relay == address(0)` fee-withholding path described above, or via any other imperfect accounting/rounding/fee-on-transfer path), and (2) the attacker must be able to submit their own swap transaction naming that same token as `inputToken` and use router calldata that requests a larger pull than their own declared `inputAmount`. Both are achievable by an unprivileged attacker (self-relay, own proof, own `externalActionMetadata`) with no privileged role required, at the cost of a normal swap transaction's gas.

I was not able to fully verify from the available code whether Hinkal enforces `feeStructure.flatFee == 0` whenever `circomData.relay == address(0)`, which affects exactly how easily/reliably the residual balance is created in the first place (this and the LI.FI router's exact calldata format for specifying pull amount would need confirmation in a live/forked test).

### Recommendation
- Bind the router call to the exact `inputAmount`: approve only `inputAmount` (not unlimited) before the router call, and revert if the router does not fully consume it (or reset/verify allowance == 0 afterward).
- Measure `balanceBefore`/`balanceAfter` for `inputToken` as well as `outputToken` in `callRouter`, and require that the input token balance decreased by exactly `inputAmount`, rejecting any swap that consumes more or less.
- Ensure fee tokens withheld when `circomData.relay == address(0)` are still forwarded somewhere deterministic (e.g., refunded into the resulting UTXO or reverted) rather than left as a stranded contract balance.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `LifiExternalAction`, a mock LI.FI router, and an ERC20 token.
2. Seed residual: perform a swap transaction through `Hinkal.transact` with `circomData.relay == address(0)` and `feeStructure.flatFee > 0` where the fee token is the input token; assert `LifiExternalAction` retains a nonzero balance of that token after the transaction (the stranded residual).
3. Attacker transaction: craft a second `Hinkal.transact` call with `deltaAmounts[0]` covering only the attacker's own principal, but with `externalActionMetadata` (mock router calldata) that pulls `principal + residual` from `LifiExternalAction` via the unlimited approval.
4. Assert: `swappedAmount` (and resulting UTXO amount credited to attacker) > amount corresponding to `-deltaAmountChanges` sent to the action for that tx, i.e. tokens leaving the action != `-deltaAmountChanges` Hinkal sent it that tx, proving the invariant break and the attacker's capture of the stranded balance.

### Citations

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L44-68)
```text
        address inputToken = circomData.erc20TokenAddresses[0];
        uint256 inputAmount = uint256(-deltaAmounts[0]);

        if (inputToken == circomData.feeStructure.feeToken) {
            inputAmount -= circomData.feeStructure.flatFee;
        }

        address outputToken = circomData.erc20TokenAddresses[1];

        require(
            circomData.slippageValues[1] != 0,
            "swap output slippage floor not set"
        );

        require(
            block.timestamp <= circomData.timeStamp + SWAP_DEADLINE_WINDOW,
            "swap expired"
        );

        uint256 swappedAmount = callRouter(
            inputToken,
            inputAmount,
            outputToken,
            circomData.externalActionData.externalActionMetadata
        );
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

**File:** contracts/Transferer.sol (L178-190)
```text
    function sendToRelay(
        address relay,
        uint256 actualAmount,
        address erc20TokenAddress
    ) internal {
        if (relay != address(0) && actualAmount > 0) {
            transferERC20TokenOrETH(
                erc20TokenAddress,
                relay,
                uint256(actualAmount)
            );
        }
    }
```

**File:** contracts/Hinkal.sol (L134-146)
```text
                // balance equation to check: CHANGE IN BALANCE SHOULD EQUAL TO
                // 1) change in off-chain utxos
                // 2) change in on-chain utxos
                require(
                    balanceDif ==
                        (
                            circomData.onChainCreation[i]
                                ? int256(0)
                                : circomData.amountChanges[i]
                        ) +
                            int256(utxoAmount),
                    "Balance Diff Should be equal to sum of onchain and offchain created commitments"
                );
```
