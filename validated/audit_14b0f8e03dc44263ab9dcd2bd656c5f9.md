### Title
`Hinkal.prooflessDeposit()` Lacks Access Control, Allowing Direct Calls That Bypass `HinkalWrapper`'s Fee Settlement - (File: contracts/Hinkal.sol)

### Summary
`Hinkal.prooflessDeposit()` is declared `public payable nonReentrant` with no restriction on the caller, while the intended entry point, `HinkalWrapper.prooflessDeposit()`, is documented as the component that "*settles the protocol fee for a proofless deposit, then forwards the deposit itself to Hinkal (which has no fee-taking logic of its own)*". A user can call `Hinkal.prooflessDeposit()` directly and skip `HinkalWrapper` entirely, avoiding the protocol fee.

### Finding Description
`HinkalWrapper.prooflessDeposit()` calls `_settleFee()` to transfer the configured `feeAmount` (ETH or ERC-20) to `feeStructure.feeRecipient` before forwarding the deposit to `Hinkal.prooflessDeposit()`. [1](#0-0) 

The actual deposit-processing logic in `Hinkal.sol`, however, has no equivalent fee logic and no restriction limiting the caller to `HinkalWrapper`. It only runs `hinkalHelper.performProoflessDepositChecks()` (array-length/amount sanity checks), then pulls tokens directly from `msg.sender` and creates on-chain commitments. [2](#0-1) 

`performProoflessDepositChecks()` in `HinkalHelper.sol` (guarded only by `onlyHinkal`, i.e. it just checks the caller is the `Hinkal` contract itself) validates lengths and non-zero amounts, but performs no fee validation whatsoever. [3](#0-2) 

Since `Hinkal.prooflessDeposit()` is `public` and unauthenticated with respect to caller identity, any EOA can call it directly instead of routing through `HinkalWrapper`, entirely skipping `_settleFee()` and therefore never paying `feeStructure.feeAmount` to `feeStructure.feeRecipient`. This exactly mirrors the referenced Vader `BasePool.mint()` finding: the "router" (`HinkalWrapper`) performs validation/fee logic that the "pool" (`Hinkal`) itself does not enforce and does not require to have been executed, so calling the low-level contract directly breaks the intended equality that every proofless deposit pays the protocol fee.

### Impact Explanation
This falls under the High-impact bucket "theft or permanent freezing of protocol/relay fees": every proofless deposit routed directly to `Hinkal.prooflessDeposit()` results in the protocol/fee recipient permanently losing the fee revenue it would otherwise have collected via `HinkalWrapper`. No shielded funds or nullifier/proof logic is affected because `prooflessDeposit` does not touch the zk-proof path, but the protocol's fee-collection guarantee is broken for any user who bypasses the wrapper.

### Likelihood Explanation
High likelihood: `Hinkal.prooflessDeposit()` is an external/public function on the main contract with no `onlyRole`, `onlyHinkalWrapper`, or similar modifier, and its interface is publicly declared in `IHinkal`. [4](#0-3) 
Any rational depositor who is aware of the two entry points has a direct financial incentive to call `Hinkal.prooflessDeposit()` instead of `HinkalWrapper.prooflessDeposit()` to avoid paying the fee, requiring no special privileges, front-running, or race condition.

### Recommendation
Add an access-control check (e.g., a `onlyHinkalWrapper` modifier or a check within `performProoflessDepositChecks`/`Hinkal.prooflessDeposit` requiring `msg.sender == hinkalWrapperAddress`, with a registered wrapper address) so that `Hinkal.prooflessDeposit()` can only be invoked through `HinkalWrapper`, ensuring fee settlement is always enforced before deposit processing.

### Proof of Concept
1. Attacker calls `Hinkal.prooflessDeposit(erc20Addresses, amounts, stealthAddressStructures, onChainEncryptedOutputs, createBlockedUtxos, orderId)` directly on the `Hinkal` contract instead of via `HinkalWrapper`.
2. `hinkalHelper.performProoflessDepositChecks()` passes (only checks array lengths and non-zero amounts). [5](#0-4) 
3. `_handleTransfersFromProoflessDeposit()` pulls exactly `amounts[i]` from the attacker with no fee deducted, and `_createProoflessDepositCommitments()` creates on-chain commitments for the full deposited amount. [6](#0-5) 
4. The attacker receives full shielded value for their deposit while the `feeStructure.feeRecipient` never receives `feeAmount`, which it would have received had the deposit gone through `HinkalWrapper._settleFee()`. [7](#0-6)

### Citations

**File:** contracts/HinkalWrapper.sol (L28-47)
```text
    function prooflessDeposit(
        address[] calldata erc20Addresses,
        uint256[] calldata amounts,
        StealthAddressStructure[] calldata stealthAddressStructures,
        bytes[] calldata onChainEncryptedOutputs,
        bool createBlockedUtxos,
        ProoflessFeeStructure calldata feeStructure,
        string calldata orderId
    ) external payable {
        uint256 ethForHinkal = _settleFee(feeStructure);
        _pullAndApproveDepositTokens(erc20Addresses, amounts);
        IHinkal(hinkal).prooflessDeposit{value: ethForHinkal}(
            erc20Addresses,
            amounts,
            stealthAddressStructures,
            onChainEncryptedOutputs,
            createBlockedUtxos,
            orderId
        );
    }
```

**File:** contracts/HinkalWrapper.sol (L49-70)
```text
    function _settleFee(
        ProoflessFeeStructure calldata feeStructure
    ) internal returns (uint256 ethForHinkal) {
        ethForHinkal = msg.value;
        if (feeStructure.feeToken == address(0)) {
            require(
                msg.value >= feeStructure.feeAmount,
                "insufficient ETH for fee"
            );
            ethForHinkal = msg.value - feeStructure.feeAmount;
            if (feeStructure.feeAmount > 0) {
                transferETH(feeStructure.feeRecipient, feeStructure.feeAmount);
            }
        } else if (feeStructure.feeAmount > 0) {
            transferERC20TokenFrom(
                feeStructure.feeToken,
                msg.sender,
                feeStructure.feeRecipient,
                feeStructure.feeAmount
            );
        }
    }
```

**File:** contracts/Hinkal.sol (L263-295)
```text
    function prooflessDeposit(
        address[] calldata erc20Addresses,
        uint256[] calldata amounts,
        StealthAddressStructure[] calldata stealthAddressStructures,
        bytes[] calldata onChainEncryptedOutputs,
        bool createBlockedUtxos,
        string calldata orderId // unused on-chain; off-chain listeners read it from calldata to match this tx to an order
    ) public payable nonReentrant {
        hinkalHelper.performProoflessDepositChecks(
            erc20Addresses,
            amounts,
            stealthAddressStructures,
            onChainEncryptedOutputs
        );

        (
            TokenWithAmount[] memory uniqueTokens,
            uint256 uniqueCount
        ) = _calcTokenChangesForProoflessDeposit(erc20Addresses, amounts);

        _handleTransfersFromProoflessDeposit(uniqueTokens, uniqueCount);

        _createProoflessDepositCommitments(
            erc20Addresses,
            amounts,
            stealthAddressStructures,
            onChainEncryptedOutputs
        );

        if (createBlockedUtxos) {
            markUtxosAsBlocked();
        }
    }
```

**File:** contracts/Hinkal.sol (L356-381)
```text
    function _handleTransfersFromProoflessDeposit(
        TokenWithAmount[] memory uniqueTokens,
        uint256 uniqueCount
    ) private {
        for (uint256 i = 0; i < uniqueCount; i++) {
            address erc20Address = uniqueTokens[i].erc20Address;
            uint256 amount = uniqueTokens[i].amount;

            uint256 balanceBefore = getERC20OrETHBalance(erc20Address);
            if (erc20Address == address(0)) balanceBefore -= msg.value;

            transferERC20TokenFromOrCheckETH(
                erc20Address,
                msg.sender,
                address(this),
                amount
            );

            uint256 balanceAfter = getERC20OrETHBalance(erc20Address);

            require(
                balanceAfter - balanceBefore == amount,
                "proofless deposit balances must be equal"
            );
        }
    }
```

**File:** contracts/HinkalHelper.sol (L37-60)
```text
    function performProoflessDepositChecks(
        address[] calldata erc20Addresses,
        uint256[] calldata amounts,
        StealthAddressStructure[] calldata stealthAddressStructures,
        bytes[] calldata onChainEncryptedOutputs
    ) external view onlyHinkal {
        require(
            amounts.length == erc20Addresses.length &&
                amounts.length == stealthAddressStructures.length &&
                amounts.length == onChainEncryptedOutputs.length,
            "amounts length must match erc20Addresses, stealthAddressStructures, onChainEncryptedOutputs length"
        );

        require(
            erc20Addresses.length <= MAX_LEAVES_PD,
            "no more than MAX_LEAVES_PD entries allowed"
        );

        for (uint256 i = 0; i < erc20Addresses.length; i++) {
            require(
                onChainEncryptedOutputs[i].length > 0,
                "Missing encrypted output for on-chain commitment"
            );
            require(amounts[i] > 0, "Amount must be greater than zero");
```

**File:** contracts/types/IHinkal.sol (L27-34)
```text
    function prooflessDeposit(
        address[] calldata erc20Addresses,
        uint256[] calldata amounts,
        StealthAddressStructure[] calldata stealthAddressStructures,
        bytes[] calldata encryptedOutputs,
        bool createBlockedUtxos,
        string calldata orderId
    ) external payable;
```
