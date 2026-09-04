### Title
Unbacked shielded UTXO minting via `DepositOnChainUtxosExternalAction` using a "double-entry" token pair sharing one real balance - (File: `contracts/Hinkal.sol`, `contracts/external-actions/DepositOnChainUtxosExternalAction.sol`)

### Summary
`Hinkal.transact` validates deposits/withdrawals per token index purely by comparing `balanceOf()` snapshots (`getBalancesForArray`) taken before and after the action, and requires `balanceDif == (onChainCreation ? 0 : amountChanges[i]) + utxoAmount` independently for each entry in `circomData.erc20TokenAddresses`. Nothing in the contracts or the circuit constrains two *distinct* addresses in that array to represent economically independent balances — the circuit's `distinctErc20AddressChecks` (in `MainEVMCircuit.circom`) only forbids the raw integers from being numerically equal. An attacker can deploy two different token addresses, `TokenA` (a real ERC20 the attacker owns) and `TokenB` (a thin alias whose `balanceOf` mirrors `TokenA`'s real balance but whose `transferFrom`/`transfer` are independently attacker-defined), and use `DepositOnChainUtxosExternalAction.runAction` to mint two shielded on-chain UTXOs of value `X` each while only `X` in real tokens ever enters the vault.

### Finding Description
The invariant claimed at `contracts/Hinkal.sol:98-146` is: for each index `i`, `balanceDif[i]` (change in `balanceOf(erc20TokenAddresses[i])` on the vault) must equal the sum of the on-chain UTXO amounts created for that same address. `oldBalances`/`newBalances` are computed once via `getBalancesForArray` (`contracts/Transferer.sol:169-176`), calling `balanceOf(address(this))` independently for every address in the caller-supplied array.

`DepositOnChainUtxosExternalAction.runAction` (`contracts/external-actions/DepositOnChainUtxosExternalAction.sol:49-83`) processes `circomData.erc20TokenAddresses` per index, pulling `tokenTotal = sum(utxoAmounts[i])` from the user via `transferERC20TokenFrom(tokenAddress, userAddress, msg.sender, tokenTotal)` and minting UTXOs of exactly that amount tagged to `tokenAddress`.

Attack construction:
- `TokenA`: a normal ERC20 the attacker actually owns/controls, with a real balance.
- `TokenB`: a distinct contract address whose `balanceOf(account)` simply forwards/mirrors `TokenA.balanceOf(account)` (so it always reports the same number as `TokenA`), but whose `transferFrom`/`transfer` are implemented independently by the attacker (e.g. a no-op returning `true` on deposit, but forwarding to `TokenA.transfer(...)` on withdrawal, i.e., the classic "two addresses, one real balance" pattern).
- Attacker sets `circomData.erc20TokenAddresses = [TokenA, TokenB]`, `onChainCreation = [true, true]`, `amountChanges = [0, 0]`, and via `externalActionData.externalActionMetadata` (the `uint256[][]`) sets `utxoAmounts[TokenA] = [X]` and `utxoAmounts[TokenB] = [X]`.
- During the action: `TokenA.transferFrom(user, vault, X)` really moves `X` real tokens into the vault, increasing `TokenA`'s real balance by `X`. `TokenB.transferFrom(user, vault, X)` is a no-op (moves nothing) but doesn't need to, because `TokenB.balanceOf(vault)` mirrors `TokenA`'s balance and will *automatically* also read `+X` after the real transfer for `TokenA`.
- Back in `Hinkal.transact`: `balanceDif[TokenA] = X` matches `utxoAmount[TokenA] = X` (real, correct). `balanceDif[TokenB] = X` (mirrored, no real asset movement) also matches `utxoAmount[TokenB] = X`. Both `require` checks at `contracts/Hinkal.sol:111-114` and `137-146` pass.
- Net effect: only `X` real tokens entered the vault, but `2X` worth of shielded on-chain UTXOs were minted and inserted into the tree (`insertCommitments`, `contracts/HinkalBase.sol:72-133`).
- The unbacked "TokenB" UTXO is later redeemable: on withdrawal, `Hinkal` calls `transferERC20TokenOrETH(TokenB, recipient, amount)` → `TokenB.transfer(...)`, which the attacker can implement to forward to `TokenA.transfer(recipient, amount)`, paying out real `TokenA` reserves that back *other users'* legitimate `TokenA` UTXOs — draining the vault.

Existing guards do not catch this: `performHinkalChecks`/`checkOnchainCreation` (`contracts/HinkalHelper.sol:181-236`) only validate `amountChanges`/`inputNullifiers` are zero for `onChainCreation`, not token-balance independence. The circuit's `distinctErc20AddressChecks` (`circuits/MainEVMCircuit.circom:171-182`) only forbids `erc20TokenAddresses[i] == erc20TokenAddresses[j]` as raw field elements — `TokenA != TokenB` as addresses, so this passes trivially. `getBalancesForArray`/`getERC20OrETHBalance` (`contracts/Transferer.sol:149-176`) blindly trust each address's `balanceOf` return value with no cross-check that the sum of all `balanceDif` entries matches a single real token movement.

### Impact Explanation
This lets an unprivileged attacker mint shielded UTXOs backed by no real asset (protocol insolvency) and later redeem them for real reserves belonging to other depositors of the mirrored real token, i.e. direct theft of other users' shielded funds / minting shielded value without backing. This matches the Critical severity category. The attack is repeatable per token pair the attacker deploys and per chain Hinkal is deployed on (e.g. Base, Arbitrum independently, each requiring its own valid proof since `chainId` is baked into `getSignedMessageHash`, `contracts/CircomDataBuilder.sol:97-132`).

### Likelihood Explanation
The attacker needs only: (1) ability to deploy arbitrary contracts (explicitly granted), (2) ability to craft `CircomData`/proof for their own UTXOs (granted), (3) use of the already-whitelisted `DepositOnChainUtxosExternalAction` external action. No privileged role is required. The only cost is deploying two small contracts and generating one valid proof for the deposit transaction (and later a proof to redeem). This is fully within the stated attacker capability and requires no race condition or privileged assumption.

### Recommendation
Do not rely solely on independent `balanceOf` snapshots per listed address. Either (a) require a global invariant that the sum of all `balanceDif` across `erc20TokenAddresses` equals the sum of all minted UTXO amounts plus off-chain `amountChanges` (so a mirrored/duplicated balance can't be double-counted across two addresses), or (b) maintain and check a running "expected balance" ledger per real token contract rather than trusting each address's self-reported `balanceOf`, or (c) restrict `erc20TokenAddresses` used in `onChainCreation`/deposit flows to a protocol-maintained allowlist of vetted token contracts instead of accepting arbitrary attacker-supplied addresses.

### Proof of Concept
Foundry test plan:
1. Deploy `TokenA` (standard ERC20, mintable to attacker).
2. Deploy `TokenB` whose `balanceOf(addr)` returns `TokenA.balanceOf(addr)`, `transferFrom` is a no-op returning `true`, and `transfer(to, amt)` calls `TokenA.transfer(to, amt)` (using vault's real `TokenA` reserve).
3. Attacker mints `X` `TokenA`, approves vault for `TokenA` and `TokenB`.
4. Call `Hinkal.transact` with `externalActionId = DepositOnChainUtxosExternalAction id`, `erc20TokenAddresses = [TokenA, TokenB]`, `onChainCreation = [true, true]`, `amountChanges = [0,0]`, metadata `utxoAmounts = [[X],[X]]`, with a locally generated valid proof.
5. Assert: `TokenA.balanceOf(vault) - preBalance == X` (only `X` real tokens entered).
6. Assert: two `NewCommitment` events emitted, one tagged `TokenA` amount `X`, one tagged `TokenB` amount `X` (total credited shielded value `2X`).
7. Assert `2X != X` (credited UTXO value exceeds real backing) — invariant `net tokens entering Hinkal == sum(amountChanges) + sum(on-chain UTXO amounts minted)` is broken (`X != 0 + 2X`).
8. Optionally, redeem the "TokenB" UTXO and show `TokenA.balanceOf(vault)` decreases by `X`, draining reserves backing other `TokenA` UTXOs. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/Hinkal.sol (L76-146)
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

            OnChainCommitment[]
                memory onChainCommitments = new OnChainCommitment[](
                    utxoSet.length
                );
            uint256 onChainCommitmentCounter = 0;
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

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L21-86)
```text
    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmounts
    ) external override onlyAllowedRecipient returns (UTXO[] memory utxoSet) {
        uint256 tokenCount = circomData.erc20TokenAddresses.length;
        require(
            tokenCount > 0 && deltaAmounts.length == tokenCount,
            "DepositOnChainUtxosExternalAction: token count mismatch"
        );

        address userAddress = circomData.originalSender;
        require(
            userAddress != address(0),
            "DepositOnChainUtxosExternalAction: Invalid originalSender"
        );

        uint256[][] memory utxoAmounts = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (uint256[][])
        );
        require(
            utxoAmounts.length == tokenCount,
            "DepositOnChainUtxosExternalAction: metadata length mismatch"
        );

        utxoSet = new UTXO[](countUtxos(utxoAmounts));

        uint256 utxoIndex = 0;
        for (uint256 i = 0; i < tokenCount; i++) {
            require(
                deltaAmounts[i] == 0,
                "DepositOnChainUtxosExternalAction: Delta amount must be zero"
            );

            address tokenAddress = circomData.erc20TokenAddresses[i];
            uint256 tokenTotal = 0;

            for (uint256 j = 0; j < utxoAmounts[i].length; j++) {
                uint256 amount = utxoAmounts[i][j];
                require(
                    amount > 0,
                    "DepositOnChainUtxosExternalAction: UTXO amount must be positive"
                );
                tokenTotal += amount;

                utxoSet[utxoIndex] = UTXO({
                    amount: amount,
                    erc20Address: tokenAddress,
                    stealthAddressStructure: circomData.stealthAddressStructure,
                    timeStamp: circomData.timeStamp + utxoIndex
                });
                utxoIndex++;
            }

            if (tokenAddress != address(0) && tokenTotal > 0) {
                transferERC20TokenFrom(
                    tokenAddress,
                    userAddress,
                    msg.sender,
                    tokenTotal
                );
            }
        }

        emit BlockedUtxosCreated();
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

**File:** contracts/HinkalHelper.sol (L181-202)
```text
            if (circomData.onChainCreation[i]) {
                require(
                    !isInternalTransaction,
                    "onChainCreation not allowed for internal transactions"
                );
                require(
                    circomData.amountChanges[i] == 0,
                    "amountChanges must be zero when onChainCreation is true"
                );
                for (
                    uint j = 0;
                    j < circomData.inputNullifiers[i].length;
                    j++
                ) {
                    require(
                        circomData.inputNullifiers[i][j] == 0,
                        "inputNullifiers must be zero when onChainCreation is true"
                    );
                }
            }
        }
    }
```

**File:** contracts/CircomDataBuilder.sol (L97-132)
```text
    function getSignedMessageHash(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData,
        uint256 emporiumMessage
    ) internal pure returns (uint256) {
        // split into two encode calls to avoid "stack too deep"
        uint256 hash1 = uint256(
            keccak256(
                abi.encode(
                    chainId,
                    verifyingContract,
                    circomData.rootHashHinkal,
                    _encodeTokenAddresses(circomData.erc20TokenAddresses),
                    _encodeAmountChanges(circomData.amountChanges),
                    circomData.timeStamp,
                    _flatUint256Matrix(circomData.inputNullifiers),
                    _flatUint256Matrix(circomData.outCommitments),
                    circomData.calldataHash,
                    emporiumMessage
                )
            )
        );
        uint256 hash2 = uint256(
            keccak256(
                abi.encode(
                    circomData.stealthAddressStructure.H1x,
                    circomData.stealthAddressStructure.H1y,
                    circomData.stealthAddressStructure.H0x,
                    circomData.stealthAddressStructure.H0y
                )
            )
        );
        return
            uint256(keccak256(abi.encode(hash1, hash2))) % CIRCOM_P;
    }
```
