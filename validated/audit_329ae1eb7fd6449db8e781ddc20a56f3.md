### Title
Unauthorised `transferFrom` via attacker-controlled `originalSender` in `DepositOnChainUtxosExternalAction` - (File: `contracts/external-actions/DepositOnChainUtxosExternalAction.sol`)

### Summary
`DepositOnChainUtxosExternalAction.runAction` pulls ERC20 tokens with `safeTransferFrom` from `circomData.originalSender` — a plain data field supplied by whoever assembles the transaction — and credits the pulled amount as brand-new "on-chain UTXOs" to the caller's own `stealthAddressStructure`. Nothing ties `originalSender` to `msg.sender` of the top-level transaction, to the `spendingPublicKey`, or to `signedMessageHash`; it is only folded into `calldataHash`, which merely proves self-consistency of the submitted calldata, not that the named address authorised the pull.

### Finding Description
The action reads the address to charge directly from calldata: [1](#0-0) 
and later executes the pull toward `msg.sender` (the Hinkal contract) using that attacker-chosen address as the `_from`: [2](#0-1) 

`originalSender` is included only in `getHashedCalldata2`, which becomes part of `calldataHash` and is checked as a public circuit signal: [3](#0-2) 
This binding only guarantees that whatever `originalSender` value the caller chose was not altered in flight — it does **not** prove the named address consented to the transfer. Unlike `spendingPublicKey`/`signedMessageHash`, which are cryptographically tied to a private key the prover must know, `originalSender` is unauthenticated plaintext that any unprivileged EOA can set to any address, including a victim's, as long as the victim has previously granted ERC20 allowance to the Hinkal contract (a realistic and common condition, since Hinkal's own deposit path has users `approve` the Hinkal contract before calling deposit functions, e.g. `_pullAndApproveDepositTokens`/`prooflessDeposit`): [4](#0-3) 

The action does not require spending any of the attacker's own shielded UTXOs (`deltaAmounts[i]` is required to be exactly `0`): [5](#0-4) 
so the attacker only needs to submit a self-consistent zk proof for an otherwise no-op transaction that carries this external action, with newly created UTXOs assigned to their own `stealthAddressStructure`.

This breaks the balance/authorization equality that Hinkal is supposed to enforce: value pulled from an on-chain address (`originalSender`) must correspond to a party that actually authorised the transfer (via `msg.sender` of the deposit, or a signature/EIP-712 message as used elsewhere, e.g. in `EmporiumUpgradeable.verifyWallet`). Here, no such authorisation is checked at all.

### Impact Explanation
Any unprivileged EOA can drain ERC20 allowance a victim previously granted to the Hinkal contract, converting the victim's tokens into shielded/on-chain UTXOs owned by the attacker. This is direct theft of user funds without requiring any owner, admin, relay, or signer key — matching the Critical impact bucket ("direct theft of shielded or in-flight user funds").

### Likelihood Explanation
Likelihood depends on victims having non-zero residual allowance to the Hinkal contract, which is a normal byproduct of the standard deposit flow (users commonly approve amounts larger than a single deposit, or approve-max, then perform multiple deposits over time, leaving allowance outstanding between transactions). No special privilege, timing, or race condition is required by the attacker — a single crafted `runAction` call suffices.

### Recommendation
Do not accept `originalSender` as free-form calldata that is trusted for `safeTransferFrom`. Either (a) require `circomData.originalSender == msg.sender` at the point the top-level `transact`/`_externalTransact` call is made (i.e., enforce it equals the actual transaction sender, similar to how `prooflessDeposit` uses `msg.sender` directly), or (b) require an explicit, freshly signed authorization (as done for `EmporiumStack.signerAddress` via EIP-712 in `EmporiumUpgradeable.verifyWallet`) binding the depositor's consent to the specific UTXOs being created.

### Proof of Concept
1. Victim (Bob) approves the Hinkal contract for `10,000 USDC` and deposits `1,000 USDC` via `prooflessDeposit`, leaving `9,000 USDC` allowance outstanding.
2. Attacker (Mallory) crafts a valid zk proof for a transaction that invokes `DepositOnChainUtxosExternalAction.runAction` with:
   - `circomData.originalSender = Bob's address`
   - `circomData.erc20TokenAddresses = [USDC]`
   - `deltaAmounts = [0]`
   - `externalActionData.externalActionMetadata` encoding `utxoAmounts = [[9000e6]]`
   - `circomData.stealthAddressStructure` pointing at Mallory's own stealth public key.
3. The action executes `transferERC20TokenFrom(USDC, Bob, Hinkal, 9000e6)` [2](#0-1) , pulling Bob's remaining allowance into the Hinkal contract.
4. A new on-chain UTXO of `9000 USDC` is created and assigned to Mallory's `stealthAddressStructure`, spendable later by Mallory alone — Bob's funds are stolen with no signature or consent from Bob.

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

**File:** contracts/Hinkal.sol (L361-381)
```text
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
