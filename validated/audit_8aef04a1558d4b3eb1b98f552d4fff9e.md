### Title
Emporium fee-token substitution drains arbitrary ERC20 balances from signer's wallet - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
The EIP-712 signature verified in `verifyWallet` binds only `emporiumMessage`, the hash of `ops`, `maxFee`, and `deadline` — it never binds `circomData.feeStructure.feeToken`. An attacker can replay a validly signed `EmporiumStack` unmodified, but pair it with a freshly crafted `CircomData` whose `feeStructure.feeToken` points at any ERC20 the victim's wallet holds, with `flatFee <= maxFee`. `payRelayFees` then unconditionally pulls `flatFee` units of that attacker-chosen token straight from the victim wallet via `doSendToRelay`, without that token ever appearing in the signed `ops`.

### Finding Description
The broken equality: the tuple the owner cryptographically authorized is `(message, hash(ops), maxFee, deadline)` via `EMPORIUM_SIGNATURE_TYPEHASH`: [1](#0-0) 
but the asset actually debited from the wallet is determined solely by `circomData.feeStructure.feeToken`/`flatFee`, fields that are **not** part of that hash and are fully attacker-controlled in the replay transaction (only `flatFee <= stack.maxFee` is checked): [2](#0-1) 

Concretely, in `payRelayFees`, when none of `circomData.erc20TokenAddresses` matches `feeStructure.feeToken` (`foundToken == false`) and `flatFee != 0`, the code takes an unconditional branch that requires only `signerAddress != address(0)` and pays `flatFee` of `feeStructure.feeToken` from the wallet — completely independent of the signed `ops` or of any token actually touched by the transaction: [3](#0-2) 

This routes through `payRelay` → `sendToRelayFromWallet` → `IHinkalWallet(signerAddress).doSendToRelay(relay, flatFee, feeToken)`: [4](#0-3) 

`doSendToRelay` on `HinkalWallet` is gated only by `onlyEmporium` (i.e., "is this the Emporium contract calling"), with no check that `feeToken`/`actualAmount` correspond to anything the wallet owner signed: [5](#0-4) 
and unconditionally performs an ERC20 transfer of the wallet's own balance to the relay: [6](#0-5) 

The attacker's fabricated `circomData` (with the swapped `feeToken`) is self-consistent for `performHinkalChecks` — `getHashedCalldata` includes `feeStructure` in its hash, but that hash is computed over the attacker's *own* chosen `circomData`, so it trivially matches `circomData.calldataHash`, and the attacker supplies a valid Groth16 proof over their own UTXOs for this exact `circomData`: [7](#0-6) 
Neither `performHinkalChecks`, `dimensionsCheck`, nor `verifyProof` constrain `feeToken` against the wallet-signature payload; that binding exists only inside the EIP-712 hash in `verifyWallet`, which omits it. Thus the wallet-owner's signature over `(ops, maxFee, deadline)` is being used to authorize debiting an arbitrary token/amount up to `maxFee` units, a field the owner never signed.

Attacker's call sequence: `Hinkal.transact` → `HinkalHelper.performHinkalChecks` (passes, attacker-consistent) → `EmporiumUpgradeable.runAction` → `verifyWallet` (passes, signature doesn't cover `feeToken`) → ops execute (can even be empty or unrelated) → `payRelayFees` → unconditional branch → `sendToRelayFromWallet` → `HinkalWallet.doSendToRelay` → `flatFee` of attacker-chosen token leaves the victim wallet to the relay address (attacker-controlled relay, or attacker acting as the `tx.origin` relay if whitelisted, or via `signerAddress==address(0)` fallback path if relay is used).

### Impact Explanation
Up to `maxFee` units of any ERC20 token the victim's `HinkalWallet` holds can be stolen per replay of a signed `EmporiumStack`, regardless of whether that token was ever part of the signed `ops`. Since `maxFee` is a raw numeric bound with no token/decimals context, the attacker can target a high-value/low-decimal token (e.g., WBTC) even though the owner intended `maxFee` to bound fees in a stablecoin. This is direct theft of wallet-held funds never authorized by the owner's signature — matching the Critical category ("direct theft of shielded or in-flight user funds" / executing an action or moving assets a wallet owner never authorized).

### Likelihood Explanation
Preconditions: attacker must harvest one validly signed `EmporiumStack` (e.g., observed on-chain or leaked off-chain before use) and the victim wallet must hold a balance of some ERC20 the attacker wants to steal. The attacker needs their own valid UTXOs/proof to satisfy Hinkal's proof check — this is fully within an unprivileged attacker's capability since they control their own deposits and can generate arbitrary-but-valid `CircomData`/proof pairs. The `usedMessages[emporiumMessage]` replay guard only prevents reusing the exact same `emporiumMessage` twice, not modifying `feeStructure.feeToken` on first use, so this fires once per unused signed stack — but each signed stack can only be exploited once (message gets marked used), limiting repeatability to the number of harvested signatures.

### Recommendation
Bind `feeStructure.feeToken`, `flatFee`, and `variableRate` into the EIP-712 hash inside `verifyWallet` (extend `EMPORIUM_SIGNATURE_TYPEHASH` to include these fields) so the wallet owner's signature explicitly authorizes the fee token and amount, not just a numeric ceiling.

### Proof of Concept
Foundry test outline:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, `HinkalWallet` (owned by victim), and two ERC20 tokens `TokenA` (used in signed `ops`) and `WETH` (never referenced by `ops`).
2. Fund the victim's `HinkalWallet` with both `TokenA` and `WETH`.
3. Victim signs a real EIP-712 `EmporiumStack{ops: [op touching only TokenA], maxFee: 100, deadline}` recovering to `signerAddress = victimWallet` per `EmporiumUpgradeable.verifyWallet`.
4. Attacker builds `CircomData` with the same `externalActionMetadata` (same `stack.v/r/s/ops/maxFee/deadline`), but sets `feeStructure.feeToken = address(WETH)`, `feeStructure.flatFee = 100`, and generates a valid Groth16 proof over their own UTXOs for this `CircomData`.
5. Call `Hinkal.transact(...)` with this proof/`CircomData`.
6. Assert: `verifyWallet` does not revert (signature check passes despite `feeToken` mismatch with `ops`); victim wallet's WETH balance decreases by exactly 100; `TokenA` balance is unaffected by the fee (only affected by ops execution, if any); confirm the equality `(feeToken, flatFee)` actually debited != anything present in `_hashEmporiumOps(stack.ops)` or the EIP-712 hash the victim signed.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L186-199)
```text
    function sendToRelayFromWallet(
        address relay,
        address signerAddress,
        uint256 relayFee,
        address feeToken
    ) internal {
        if (relayFee > 0) {
            IHinkalWallet(signerAddress).doSendToRelay(
                relay,
                relayFee,
                feeToken
            );
        }
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L247-259)
```text
        if (!foundToken && feeStructure.flatFee != 0) {
            require(
                signerAddress != address(0),
                "Gas Token in Emporium is not found"
            );

            payRelay(
                circomData.relay,
                signerAddress,
                feeStructure.flatFee,
                feeStructure.feeToken
            );
        }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L318-328)
```text
        bytes32 hashedMessage = _hashTypedDataV4(
            keccak256(
                abi.encode(
                    EMPORIUM_SIGNATURE_TYPEHASH,
                    circomData.emporiumMessage,
                    _hashEmporiumOps(stack.ops),
                    stack.maxFee,
                    stack.deadline
                )
            )
        );
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L346-348)
```text
        if (circomData.feeStructure.flatFee > stack.maxFee) {
            revert FeeExceedsSignedMax();
        }
```

**File:** contracts/external-actions/emporium/HinkalWallet.sol (L36-42)
```text
    function doSendToRelay(
        address relay,
        uint256 actualAmount,
        address erc20TokenAddress
    ) external onlyEmporium {
        sendToRelay(relay, actualAmount, erc20TokenAddress);
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

**File:** contracts/CircomDataBuilder.sol (L37-54)
```text
    function getHashedCalldata2(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.hookData,
                        circomData.encryptedOutputs,
                        circomData.onChainEncryptedOutput,
                        circomData.feeStructure,
                        circomData.onChainCreation,
                        circomData.originalSender,
                        circomData.extraData
                    )
                )
            );
    }
```
