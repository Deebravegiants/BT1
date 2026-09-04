### Title
Balance-snapshot accounting in `Hinkal.transact`/`EmporiumUpgradeable.runAction` double-counts a single real balance across two aliased `erc20TokenAddresses` entries, minting shielded UTXO value without backing - (File: contracts/Hinkal.sol, contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`Hinkal.transact` and `EmporiumUpgradeable.runAction` both derive the amount of value that "entered" the vault purely from `balanceOf` deltas taken independently for each entry of `circomData.erc20TokenAddresses`. If an attacker supplies two distinct contract addresses that both expose `balanceOf`/`transfer` reading and mutating the *same* underlying storage slot (a "double-entry point" token), a single real balance increase is observed and credited twice - once per address - so `balanceDif == amountChanges[i] + utxoAmount` is satisfied for both indices even though only one real unit of value actually moved.

### Finding Description
The equality being tested is: `real value received by Hinkal == sum(amountChanges) + sum(minted on-chain UTXO amounts)`. Both `Hinkal.transact` and `EmporiumUpgradeable.runAction` compute this per `erc20TokenAddresses` index using independent `getBalancesForArray`/`getERC20OrETHBalance` snapshots: [1](#0-0) [2](#0-1) 

and the per-index check: [3](#0-2) 

The only structural constraint on `erc20TokenAddresses` is that entries be pairwise-distinct *addresses*, enforced in the circuit: [4](#0-3) 

Nothing - neither the circuit nor the Solidity checks - constrains two different addresses from reading/writing the same underlying balance. If the attacker deploys two token addresses `TokenA` and `TokenB` whose `balanceOf`/transfer logic forwards to one shared storage location, a single real transfer of `X` into that shared balance is observed as `+X` for `TokenA` and `+X` for `TokenB` independently in both `EmporiumUpgradeable.runAction`'s before/after snapshot: [5](#0-4) 

and in `Hinkal.transact`'s outer snapshot. `handleOut` then mints one UTXO of amount `X` per aliased address, i.e. `2X` of shielded value is credited from a single real `X` movement: [6](#0-5) 

Because `balanceDif[i]` and `utxoAmount[i]` are both derived from the same aliased read for each `i`, the per-index equality `balanceDif == amountChanges[i] + utxoAmount` holds trivially for *both* indices - the check cannot detect that the two "independent" balances are in fact one. `amountChanges`/`erc20TokenAddresses` values are proof-bound public inputs (`formBasicInput`), so the attacker must generate their own valid proof for this exact aliased address pair rather than mutate an existing proof's calldata - which is fully within the stated attacker capabilities (self-generated proofs, own tokens, own external endpoints/calldata): [7](#0-6) 

None of the listed guards (`performHinkalChecks`, `dimensionsCheck`, `checkOnchainCreation`, `rootHashExists`, `insertNullifiers`) inspect the *economic* independence of `erc20TokenAddresses` entries; they only check structural/dimensional consistency and address-level distinctness.

### Impact Explanation
The attacker (or any future depositor into a token exhibiting this "multiple address / shared balance" pattern - a documented real-world weird-ERC20 behavior, not merely hypothetical) can cause Hinkal to mint on-chain shielded UTXOs worth `N * X` while only `X` of real value entered the contract, where `N` is the number of aliased addresses included in one `erc20TokenAddresses` array (bounded by `dimensions.tokenNumber`). If the aliased token is ever shared with other depositors (i.e., its pooled balance in Hinkal includes other users' funds), the attacker can subsequently redeem the excess phantom UTXOs against the shared pool, draining other users' real deposits - this is Critical: minting shielded value without backing / protocol insolvency. The attack is repeatable per token pair deployed and scales with the number of aliased entries used per call.

### Likelihood Explanation
Preconditions: the attacker needs a token whose `balanceOf`/transfer-affecting calls are exposed under two distinct contract addresses sharing one real balance (attacker-deployable for PoC purposes, and a known real-world weird-ERC20 category). No privileged role, relay, or victim cooperation is required to trigger the mis-accounting itself - `erc20TokenAddresses`, `amountChanges`, the token, and `externalActionData` are all attacker-controlled per the question's threat model. The only added precondition for turning this into fund theft from other users is that the aliased token later carries other users' deposits, which is outside the attacker's direct control in a single transaction but is exactly the scenario this class of bug is designed to protect against.

### Recommendation
Do not rely solely on independent `balanceOf` snapshots per `erc20TokenAddresses` index. Either (a) require and verify per-token uniqueness of the underlying balance (e.g., disallow duplicate "canonical" token identity via an allow-list/registry rather than raw address distinctness), or (b) compute a single aggregate balance check across the whole snapshot rather than crediting UTXOs per index when the same physical balance may be observed through multiple addresses, or (c) restrict `erc20TokenAddresses` to a protocol-curated allow-list of vetted tokens known not to exhibit multi-address/shared-balance behavior.

### Proof of Concept
1. Deploy `Vault` holding a `mapping(address=>uint256) balances` and an internal `_move(from,to,amount)`.
2. Deploy `TokenA` and `TokenB`, each a thin ERC20 wrapper whose `balanceOf`/`transfer` forward to `Vault` (both addresses reflect the same `Vault.balances` mapping).
3. Register a benign `Emporium` external action; craft `circomData` with `erc20TokenAddresses = [TokenA, TokenB]`, `amountChanges = [0,0]`, `onChainCreation = [true,true]`, and an `EmporiumOperation` whose stateless call performs a single `Vault._move`/mint of `X` credited to the Emporium contract's balance.
4. Generate a locally valid proof for this `CircomData` and call `Hinkal.transact`.
5. Assert: `Vault.balances[hinkal]` (or Emporium's real balance) increased by exactly `X`, but the sum of minted on-chain UTXO amounts (`utxoSet[0].amount + utxoSet[1].amount`) equals `2X`, and each per-index `require(balanceDif == amountChanges[i] + utxoAmount)` in `Hinkal.transact` passed without reverting - demonstrating `real value received (X) < credited shielded UTXO value (2X)`.

### Citations

**File:** contracts/Hinkal.sol (L76-90)
```text
            UTXO[] memory utxoSet;

            uint256[] memory oldBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            if (circomData.externalActionData.externalActionId == 0) {
                _internalTransact(circomData);
            } else {
                utxoSet = _externalTransact(circomData);
            }

            uint256[] memory newBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );
```

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

**File:** contracts/Transferer.sol (L149-176)
```text
    function getERC20OrETHBalance(
        address _erc20TokenAddress
    ) internal view returns (uint256) {
        if (_erc20TokenAddress == address(0)) {
            return address(this).balance;
        } else {
            IERC20 outToken = IERC20(_erc20TokenAddress);
            return outToken.balanceOf(address(this));
        }
    }

    function getBalancesForArrayMemory(
        address[] memory erc20TokenAddresses
    ) internal view returns (uint256[] memory balances) {
        balances = new uint256[](erc20TokenAddresses.length);
        for (uint64 i; i < erc20TokenAddresses.length; i++) {
            balances[i] = getERC20OrETHBalance(erc20TokenAddresses[i]);
        }
    }

    function getBalancesForArray(
        address[] calldata erc20TokenAddresses
    ) internal view returns (uint256[] memory balances) {
        balances = new uint256[](erc20TokenAddresses.length);
        for (uint64 i; i < erc20TokenAddresses.length; i++) {
            balances[i] = getERC20OrETHBalance(erc20TokenAddresses[i]);
        }
    }
```

**File:** circuits/MainEVMCircuit.circom (L171-182)
```text
  component distinctErc20AddressChecks[tokenCount * (tokenCount-1)/2];
  var index = 0;
  for (var i =0; i< tokenCount-1;i++){
    for (var j = i+1; j< tokenCount; j++)
    {
      distinctErc20AddressChecks[index] = IsEqual();
      distinctErc20AddressChecks[index].in[0] <== erc20TokenAddresses[i];
      distinctErc20AddressChecks[index].in[1] <== erc20TokenAddresses[j];
      distinctErc20AddressChecks[index].out === 0;
      index++;
    }
  }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-151)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        verifyWallet(stack, circomData);

        for (uint256 i = 0; i < stack.ops.length; i++) {
            EmporiumOperation memory op = stack.ops[i];

            bool success;
            bytes memory err;

            // CASE 1: Stateful Interaction
            if (op.invokeWallet && stack.signerAddress != address(0)) {
                (success, err) = IHinkalWallet(stack.signerAddress)
                    .callHinkalWallet(op.endpoint, op.callData, op.value);
            }
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

            if (!success) {
                revert CallFailed(err);
            }
        }

        payRelayFees(circomData, stack.signerAddress, deltaAmountChanges);

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L162-180)
```text
    function handleOut(
        int256 balanceChange,
        CircomData calldata circomData,
        uint256 i
    ) internal returns (UTXO memory outUtxo) {
        // total change can be less than zero if there was some balance before the call -> that's why we have <=
        if (balanceChange <= 0) {
            return outUtxo;
        }

        transferERC20TokenOrETH(
            circomData.erc20TokenAddresses[i],
            msg.sender,
            uint256(balanceChange)
        );

        outUtxo = UTXO(
            uint256(balanceChange),
            circomData.erc20TokenAddresses[i],
```

**File:** contracts/CircomDataBuilder.sol (L180-219)
```text
    function formBasicInput(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData,
        uint256[] memory input,
        uint256 index,
        uint256 emporiumMessage
    ) internal pure returns (uint256[] memory) {
        // 1) First we list public inputs as in the body of the main template (not the one with exact dimensions)
        input[index++] = circomData.stealthAddressStructure.H1x;
        input[index++] = circomData.stealthAddressStructure.H1y;
        input[index++] = circomData.stealthAddressStructure.stealthAddress;
        input[index++] = emporiumMessage; // this is for Emporium message signature verification

        // 2) Then we list the private inputs as in the body of the main template
        input[index++] = circomData.rootHashHinkal;
        input[index++] = getSignedMessageHash(
            chainId,
            verifyingContract,
            circomData,
            emporiumMessage
        );

        for (uint16 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            input[index++] = uint256(
                uint160(circomData.erc20TokenAddresses[i])
            );
        }

        for (uint16 i = 0; i < circomData.amountChanges.length; i++) {
            require(
                circomData.amountChanges[i] < MAX_AMOUNT &&
                    circomData.amountChanges[i] > -1 * MAX_AMOUNT,
                "amount changed is too large"
            );

            input[index++] = circomData.amountChanges[i] >= 0
                ? uint256(circomData.amountChanges[i])
                : CIRCOM_P - uint256(-circomData.amountChanges[i]);
        }
```
