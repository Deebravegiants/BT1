### Title
`prooflessDeposit` accepts unaccounted-for `msg.value` when no ETH entry is present in `erc20Addresses`, permanently freezing sent ETH - (File: `contracts/Hinkal.sol`)

### Summary
`Hinkal.prooflessDeposit` is `payable` but never validates that `msg.value` corresponds to anything in the caller-supplied `erc20Addresses`/`amounts` arrays. If the caller sends ETH (`msg.value > 0`) while `erc20Addresses` contains no `address(0)` entry, that ETH is accepted, added to the contract's balance, but never checked, transferred to a recipient, or represented by any on-chain commitment/UTXO — breaking the equality between ETH actually received and value the protocol has committed to a spendable leaf.

### Finding Description
`prooflessDeposit` computes `uniqueTokens` strictly from the caller-supplied `erc20Addresses`/`amounts` and only iterates over those tokens when pulling/checking transfers: [1](#0-0) 

The actual value-moving/validating step, `_handleTransfersFromProoflessDeposit`, only calls `transferERC20TokenFromOrCheckETH` (which enforces `msg.value == _value` for the ETH branch) for tokens that appear in `uniqueTokens`: [2](#0-1) [3](#0-2) 

If `erc20Addresses` contains no `address(0)` entry, the ETH branch of `transferERC20TokenFromOrCheckETH` is never reached at all, so no check against `msg.value` ever executes. `hinkalHelper.performProoflessDepositChecks` (the pre-flight validation for this function) also never inspects `msg.value`: [4](#0-3) 

Consequently, any ETH sent alongside a `prooflessDeposit` call whose `erc20Addresses` array omits `address(0)` is silently absorbed into the contract's ETH balance with no corresponding on-chain commitment created in `_createProoflessDepositCommitments`, and no `amountChanges`/`utxoAmount` entry in the `transact` balance equation ever accounts for it either (that equation only runs for `transact`, not `prooflessDeposit`, and only over `circomData.erc20TokenAddresses`, which a spender controls, not the depositor): [5](#0-4) 

There is no admin sweep/rescue function found in the codebase that could recover this stray ETH; it becomes permanently unbacked and unspendable, sitting in the contract's balance without a nullifier/UTXO ever referencing it.

### Impact Explanation
This breaks the fundamental Hinkal invariant that every unit of on-chain asset value is backed by exactly one spendable leaf/commitment. ETH accepted this way is real user value that enters the contract but is never turned into a UTXO the depositor (or anyone) can later spend via `transact`, and there is no recovery path. This is a permanent freezing of user funds, which the rules classify as Critical impact.

### Likelihood Explanation
The path is reachable by any unprivileged EOA directly calling the public, payable `prooflessDeposit` function with a trivially constructable `erc20Addresses` array that omits `address(0)` while attaching `msg.value`. No relayer, admin, or special permission is required — likelihood is high, limited only by whether integrators normally forget to zero out `msg.value` when depositing purely-ERC20 baskets, or whether front-ends miscompute the value to attach (e.g. when combined with `HinkalWrapper`'s fee-forwarding, which also never checks that leftover `ethForHinkal` corresponds to an ETH entry in `erc20Addresses`).

### Recommendation
In `Hinkal.prooflessDeposit` (and in `_handleTransfersFromProoflessDeposit`), explicitly validate that `msg.value` equals the sum of amounts for any `address(0)` entries in `erc20Addresses`, and require `msg.value == 0` when no such entry exists — mirroring the strict-equality pattern already used in `transferERC20TokenFromOrCheckETH`. Add this check inside `HinkalHelper.performProoflessDepositChecks` or at the top of `prooflessDeposit` before any transfers occur.

### Proof of Concept
1. Attacker (or a misconfigured integrator) calls `Hinkal.prooflessDeposit(erc20Addresses, amounts, stealthAddressStructures, onChainEncryptedOutputs, false, "order")` with `erc20Addresses = [USDC]`, `amounts = [1000]`, and attaches `msg.value = 1 ether`.
2. `performProoflessDepositChecks` passes (it never looks at `msg.value`).
3. `_calcTokenChangesForProoflessDeposit` returns `uniqueTokens = [{USDC, 1000}]`; `_handleTransfersFromProoflessDeposit` only processes the USDC entry — the ETH branch of `transferERC20TokenFromOrCheckETH` is never invoked.
4. The transaction succeeds: USDC is pulled and a valid commitment is created for it, and 1 ETH is now sitting in the `Hinkal` contract's balance, uncommitted and unrecoverable — permanently frozen.

### Citations

**File:** contracts/Hinkal.sol (L97-146)
```text
            for (uint64 i; i < circomData.erc20TokenAddresses.length; i++) {
                int256 balanceDif;

                if (circomData.erc20TokenAddresses[i] == address(0)) {
                    balanceDif =
                        int256(newBalances[i]) +
                        int256(msg.value) -
                        int256(oldBalances[i]);
                } else {
                    balanceDif =
                        int256(newBalances[i]) -
                        int256(oldBalances[i]);
                }
                // balance inequality to check that minimum amount of token is received/given
                require(
                    balanceDif >= circomData.slippageValues[i],
                    "slippage param is violated"
                );

                uint256 utxoAmount = 0;
                for (uint j = 0; j < utxoSet.length; j++) {
                    if (
                        utxoSet[j].erc20Address ==
                        circomData.erc20TokenAddresses[i]
                    ) {
                        utxoAmount += utxoSet[j].amount;

                        onChainCommitments[
                            onChainCommitmentCounter
                        ] = createOnchainCommitment(
                            utxoSet[j],
                            circomData.onChainEncryptedOutput
                        );
                        onChainCommitmentCounter++;
                    }
                }

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

**File:** contracts/Transferer.sol (L111-128)
```text
    function transferERC20TokenFromOrCheckETH(
        address _contractAddress,
        address _from,
        address _to,
        uint256 _value
    ) internal {
        if (_contractAddress == address(0)) {
            require(
                msg.value == _value,
                "msg.value doesn't match needed amount"
            );
            if (_to != address(this)) {
                transferETH(_to, _value);
            }
        } else {
            transferERC20TokenFrom(_contractAddress, _from, _to, _value);
        }
    }
```

**File:** contracts/HinkalHelper.sol (L37-62)
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
        }
    }
```
