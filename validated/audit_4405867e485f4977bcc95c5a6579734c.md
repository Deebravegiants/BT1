### Title
Unauthorized `transferFrom` of user funds via attacker-controlled `originalSender` in `DepositOnChainUtxosExternalAction` - (File: `contracts/external-actions/DepositOnChainUtxosExternalAction.sol`)

### Summary
`DepositOnChainUtxosExternalAction.runAction()` pulls ERC20 tokens from `circomData.originalSender` with no check that this address matches the actual transaction sender or any signer authenticated by the circuit. Since `originalSender` is an ordinary field the prover freely chooses (it is merely hashed into `calldataHash`, not tied to any signature from the token owner), any address can build its own valid proof, set `originalSender` to a victim who has an outstanding ERC20 allowance to this contract, and drain that allowance into UTXOs that only the attacker controls.

### Finding Description
In `runAction`, the deposit source is taken directly from calldata rather than from `msg.sender`/a verified signer: [1](#0-0) 

and the actual pull happens here: [2](#0-1) 

`circomData.originalSender` only feeds into the calldata hash used for calldata integrity, not into any ownership/signature check: [3](#0-2) 

The EdDSA signature verified inside the ZK circuit (`SignatureVerifier`) only authenticates the shielded `spendingPublicKey` that will own the newly created UTXOs — it says nothing about who the ERC20 tokens are pulled from. The circuit's balance equation (`inTotal + amountChanges[i] === outTotal`) is enforced only over the *shielded* input/output UTXOs; it has no visibility into, or constraint on, the plaintext ERC20 `transferFrom` performed inside the external action, and `deltaAmounts[i]` is explicitly required to be `0` for every token here: [4](#0-3) 

so the on-chain amount-changed accounting in `Hinkal._externalTransact` (which only handles negative deltas) never even looks at the tokens actually withdrawn from `userAddress`.

By contrast, the protocol's own internal deposit path explicitly enforces that the actual caller is the one funding the deposit: [5](#0-4) 

That same self-authorization check is missing from `_externalTransact`: [6](#0-5) 

`ExternalActionBaseV2.onlyAllowedRecipient` only checks that `msg.sender` is the trusted `Hinkal`/router contract, not who benefits from the shielded UTXOs or whose tokens are moved: [7](#0-6) 

Because this contract is meant to be a normal deposit entry point (per its own docstring, "Deposits tokens into Hinkal…"), users are expected to grant it an ERC20 allowance in the ordinary course of using the product. Any attacker can then submit their own self-generated proof (using their own shielded spending key/output stealth address) with `circomData.originalSender` set to any address that currently has a non-zero allowance for this contract, sweeping that allowance into UTXOs that decrypt only to the attacker.

### Impact Explanation
This is a direct, unauthorized `transferFrom` of a victim's ERC20 balance/allowance that a wallet owner never signed off on for this specific transaction — funds are stolen and converted into shielded value controlled solely by the attacker. This matches the Critical impact category: direct theft of user funds via an unauthorized asset movement not authorized by the token owner.

### Likelihood Explanation
Likelihood is high for any user who has an active allowance to this specific external-action contract (the normal state for anyone who has used, or is in the middle of using, this deposit flow — e.g., approve-then-deposit UX, or apps that set a standing/large allowance for convenience). The attacker needs no special privilege: they only need to generate their own valid proof (fully within their control, since it only needs to authenticate their own shielded keys) and call the public `transact`/deposit entry point on `Hinkal.sol`.

### Recommendation
Require that `circomData.originalSender == msg.sender` (i.e., the actual EOA/contract initiating the transaction) before pulling funds in `DepositOnChainUtxosExternalAction.runAction`, mirroring the check already used in `Hinkal._internalTransact` ("Deposit should come from the sender"). Alternatively, bind `originalSender` to a value authenticated by a signature from that address (similar to how `EmporiumUpgradeable` recovers and validates `stack.signerAddress`), so that no third party can name an arbitrary victim as the token source.

### Proof of Concept
1. Victim `V` approves `DepositOnChainUtxosExternalAction` for `1000 USDC` (e.g., as part of a normal deposit flow they intend to complete later, or via a dApp default/standing approval).
2. Attacker `A` builds their own valid `MainEVMCircuit` proof using their own `spendingPublicKey`/`nullifyingPrivateKey` (no input UTXOs needed since this is a pure deposit; `amountChanges[i] = 0` for all tokens, satisfying `deltaAmounts[i] == 0` in the external action).
3. `A` sets `circomData.externalActionData.externalActionId` to the id mapped to `DepositOnChainUtxosExternalAction`, `circomData.originalSender = V`, `circomData.erc20TokenAddresses = [USDC]`, and `externalActionMetadata` encoding `utxoAmounts = [[1000e6]]`, with `stealthAddressStructure` pointing at `A`'s own shielded address.
4. `A` calls `Hinkal.transact(...)`. The proof verifies (it only attests to `A`'s own shielded state), the root hash check passes trivially since no input UTXOs are spent, and `Hinkal._externalTransact` calls `DepositOnChainUtxosExternalAction.runAction`.
5. Inside `runAction`, `transferERC20TokenFrom(USDC, V, msg.sender, 1000e6)` executes, pulling `V`'s tokens using `V`'s pre-existing allowance, and mints UTXO commitments controlled only by `A`.
6. `V`'s `1000 USDC` is gone; `A` now holds a shielded balance of `1000 USDC` inside Hinkal, without `V` ever signing or authorizing this specific transaction.

### Citations

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L31-35)
```text
        address userAddress = circomData.originalSender;
        require(
            userAddress != address(0),
            "DepositOnChainUtxosExternalAction: Invalid originalSender"
        );
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L49-53)
```text
        for (uint256 i = 0; i < tokenCount; i++) {
            require(
                deltaAmounts[i] == 0,
                "DepositOnChainUtxosExternalAction: Delta amount must be zero"
            );
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L75-82)
```text
            if (tokenAddress != address(0) && tokenTotal > 0) {
                transferERC20TokenFrom(
                    tokenAddress,
                    userAddress,
                    msg.sender,
                    tokenTotal
                );
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

**File:** contracts/Hinkal.sol (L177-187)
```text
            if (deltaAmountChange > 0) {
                require(
                    circomData.externalActionData.externalAddress == msg.sender,
                    "Deposit should come from the sender"
                );
                transferERC20TokenFromOrCheckETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    address(this),
                    uint256(circomData.amountChanges[i])
                );
```

**File:** contracts/Hinkal.sol (L234-261)
```text
    function _externalTransact(
        CircomData calldata circomData
    ) internal returns (UTXO[] memory) {
        require(
            externalActionMap[circomData.externalActionData.externalActionId] ==
                circomData.externalActionData.externalAddress &&
                circomData.externalActionData.externalAddress != address(0),
            "Unknown externalAddress"
        );

        int256[] memory deltaAmountChanges = new int256[](
            circomData.erc20TokenAddresses.length
        );
        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            deltaAmountChanges[i] = _calculateDeltaAmount(circomData, i);
            if (deltaAmountChanges[i] < 0) {
                transferERC20TokenOrETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    uint256(-deltaAmountChanges[i])
                );
            }
        }

        return
            IExternalActionV2(circomData.externalActionData.externalAddress)
                .runAction(circomData, deltaAmountChanges);
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
