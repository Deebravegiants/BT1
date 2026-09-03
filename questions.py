import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 20
# todo: the GitLab namespace/project path, for example group/project
SOURCE_REPO = 'Hinkal-Protocol/Hinkal-Contracts-Circuits'
# todo: the name of the repository
REPO_NAME = 'Hinkal-Contracts-Circuits'

run_number = os.environ.get('GITHUB_RUN_NUMBER', '0')


def get_cyclic_index(run_number, max_index=100):
    """Convert run number to a cyclic index between 1 and max_index"""
    return (int(run_number) - 1) % max_index + 1


def load_repository_urls():
    """Load repository URLs from repositories.json."""
    repo_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repositories.json")
    if not os.path.exists(repo_file):
        return []

    try:
        with open(repo_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    return [url for url in data if isinstance(url, str) and url.strip()]


if run_number == "0":
    BASE_URL = f"https://deepwiki.com/{SOURCE_REPO}"
else:
    repository_urls = load_repository_urls()
    if repository_urls:
        run_index = get_cyclic_index(run_number, len(repository_urls))
        BASE_URL = repository_urls[run_index - 1]
    else:
        BASE_URL = f"https://deepwiki.com/{SOURCE_REPO}"

scope_files = [
    # =================================================================================
    # LENS: VALUE CONSERVATION AND PROOF BINDING.
    # Hinkal is a shielded-UTXO pool. Every file below sits on the path from attacker-
    # supplied calldata - CircomData, Dimensions, a Groth16 proof, external-action
    # metadata, hook addresses, deposit arrays - to one of three decisions: does the
    # proof constrain exactly the values the chain acts on, does value entering or
    # leaving Hinkal equal the shielded value created or destroyed, and can a leaf be
    # spent exactly once. A question belongs here only if it can be closed by an
    # equality that must hold between what the circuit constrained and what the
    # contracts moved.
    # =================================================================================

    # -- The entrypoint and the balance equation ---------------------------------------
    # `transact` runs performHinkalChecks -> verifyProof -> rootHashExists -> hooks ->
    # internal or external transfer -> balanceDif == amountChanges + utxoAmount ->
    # insertNullifiers -> insertCommitments. `prooflessDeposit` skips the proof and
    # mints on-chain UTXOs from msg.value / transferFrom. Every equality lives here.
    "contracts/Hinkal.sol",
    "contracts/HinkalBase.sol",
    "contracts/HinkalWrapper.sol",
    "contracts/Transferer.sol",
    "contracts/TransfererBase.sol",

    # -- What the proof actually covers -------------------------------------------------
    # CircomDataBuilder builds calldataHash and signedMessageHash and the public-input
    # vector in a fixed order; HinkalHelper checks lengths against Dimensions, relay,
    # originalSender and onChainCreation; VerifierFacade picks the verifier from
    # (tokenNumber, nullifierAmount, outputAmount, externalActionId). Anything acted on
    # that is not inside these hashes is unproven input riding a valid proof.
    "contracts/CircomDataBuilder.sol",
    "contracts/HinkalHelper.sol",
    "contracts/VerifierFacade.sol",
    "contracts/Constants.sol",
    "contracts/RelayStore.sol",

    # -- The commitment tree and its truncated-path semantics ---------------------------
    # Merkle stores one frontier node per level and a root only at batch ends; the
    # circuit's MerkleRootCalculator treats a zero sibling as "stop here". The two must
    # agree on exactly which (leaf, root) pairs exist.
    "contracts/Merkle.sol",
    "contracts/MerkleBase.sol",

    # -- Money that leaves Hinkal into caller-steered contracts -------------------------
    # External actions receive -delta tokens BEFORE runAction, execute caller-supplied
    # metadata (arbitrary calls in Emporium, arbitrary router calldata in LiFi, standing
    # approvals in DepositOnChainUtxos) and hand back a UTXO set that Hinkal credits.
    "contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol",
    "contracts/external-actions/emporium/upgradeable/EmporiumStorage.sol",
    "contracts/external-actions/emporium/EmporiumStack.sol",
    "contracts/external-actions/emporium/HinkalWallet.sol",
    "contracts/external-actions/swaps/ExternalActionSwap.sol",
    "contracts/external-actions/swaps/LifiExternalAction.sol",
    "contracts/external-actions/DepositOnChainUtxosExternalAction.sol",
    "contracts/external-actions/ExternalActionBaseV2.sol",
    "contracts/external-actions/ExternalActionBaseUpgradeable.sol",
    "contracts/lib/UTXOLib.sol",

    # -- Deployment, ownership and shared types ---------------------------------------
    "contracts/HinkalFactory.sol",
    "contracts/HinkalFactoryDeployer.sol",
    "contracts/OwnerHinkal.sol",
    "contracts/OwnerHinkalUpgradeable.sol",
    "contracts/types/CircomData.sol",
    "contracts/types/UTXO.sol",
    "contracts/types/Dimensions.sol",
    "contracts/types/StealthAddressStructure.sol",
    "contracts/types/ProoflessFeeStructure.sol",
    "contracts/types/TokenWithAmount.sol",
    "contracts/types/IHinkal.sol",
    "contracts/types/IHinkalBase.sol",
    "contracts/types/IHinkalHelper.sol",
    "contracts/types/IExternalAction.sol",
    "contracts/types/IExternalActionV2.sol",
    "contracts/types/ITransactHook.sol",
    "contracts/types/IHinkalWallet.sol",
    "contracts/types/IRelayStore.sol",
    "contracts/types/IMerkle.sol",
    "contracts/types/IVerifier.sol",
    "contracts/types/IVerifierFacade.sol",
    "contracts/types/IWrapper.sol",
    "contracts/types/IPoseidon2.sol",
    "contracts/types/IPoseidon4.sol",

    # -- The circuits: what a valid proof actually asserts -----------------------------
    # MainEVMCircuit: nullifier = Poseidon(commitment, Poseidon(key, commitment)),
    # commitment = Poseidon4(amount, token, stealth, ts) zeroed when amount == 0,
    # root check disabled when amount == 0, inTotal + amountChanges === outTotal.
    # MainEVMCircuitMin proves only knowledge of messageSeed.
    "circuits/MainEVMCircuit.circom",
    "circuits/MainEVMCircuitMin.circom",
    "circuits/MerkleRootCalculator.circom",
    "circuits/NullifierCalculator.circom",
    "circuits/OriginalCommitmentCalculator.circom",
    "circuits/Signature.circom",
    "circuits/SignatureVerifier.circom",
    "circuits/StealthAddressCalculator.circom",
    "circuits/StealthAddressCompressor.circom",
    "circuits/PointCompressor.circom",
    "circuits/OverflowPreventer.circom",
    "circuits/ConditionalOverflowPreventer.circom",
    "circuits/BabyJubjubSubgroupCheck.circom",

    # =================================================================================
    # NOT IN THIS VARIANT:
    # * contracts/verifiers/** - snarkJS / Circom-Make generated Groth16 verifiers and
    #   wrappers. Generated code, out of scope.
    # * contracts/types/IVerifierEVM*.sol - generated per-dimension interfaces.
    # * circuits/BabyJubjubConstants.circom - generated constant table.
    # * README.md, *.py, *.json, *.toml and any test, mock or deployment file.
    # =================================================================================
]


target_scopes = [
    "Critical. THE MIN CIRCUIT TURNS EMPORIUM INTO A PERMISSIONLESS EXECUTOR. `CircomDataBuilder.formInputForCircom` selects `formInputEmporiumMin` whenever `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`; `MainEVMCircuitMin` proves only `message == Poseidon(messageSeed)` - no key, no nullifier, no root. `EmporiumUpgradeable.runAction` then decodes an `EmporiumStack` with `signerAddress == 0` (so `verifyWallet` checks only `usedMessages`) and executes every `op.endpoint.call{value: op.value}(op.callData)` from Emporium itself, while the balance loop iterates an EMPTY token list. Enumerate what Emporium's `msg.sender` identity and balances are worth: ETH and ERC20 parked there by any earlier flow, approvals that persist after the call, and every contract whose `onlyAllowedRecipient`, `onlyOwner` or router trust names Emporium. Identity: set of assets Emporium can move in a transaction == set of assets accounted in `balancesBefore` / `balancesAfter`.",

    "Critical. EXTERNAL ACTIONS ACCOUNT ONLY FOR THE TOKENS THE CALLER LISTS. `LifiExternalAction.callRouter` calls `approveUnlimited(inputToken, router)` and then `router.call(externalActionMetadata)` with fully caller-controlled calldata, and `inputAmount` is never passed to the router for ERC20 input - the calldata decides how much is pulled. `ExternalActionSwap.swap` deducts `totalFee` from `amountToSendToHinkal` but `sendToRelay` silently no-ops when `circomData.relay == address(0)`, stranding the fee inside the action; `EmporiumUpgradeable.handleOut` returns only the positive `balanceChange`, so any pre-existing balance stays. Show that value the protocol itself parks in an action (stranded fees, router refunds, partial fills, `-delta` tokens the caller then omits) is pulled out by the next unprivileged caller and credited as their UTXO. Identity: tokens leaving an action in a transaction == the `-deltaAmountChanges` Hinkal sent to it in that same transaction.",

    "Critical. POSITIVE `amountChanges` IN AN EXTERNAL TRANSACTION IS A DEPOSIT WITH NO PAYER. In `Hinkal._externalTransact` only negative deltas are transferred to the action; a positive `amountChanges[i]` is satisfied by whatever makes `balanceDif` rise - an Emporium op that `transfer`s Emporium's own balance to Hinkal, a LiFi router paying Hinkal directly, an ERC777 hook. The circuit then enforces `inTotal + amountChanges === outTotal` and mints `amountChanges[i]` of shielded value with no on-chain UTXO and no `transferFrom` from the prover. Show a source of tokens reachable by an unprivileged caller (any residual in Emporium or the swap action, any allowance those contracts hold, any refund a router sends) that is turned into shielded balance through a positive delta. Identity: every positive `amountChanges[i]` == value the prover paid from an account the prover controls.",

    "Critical. THE BALANCE EQUATION IS THE ONLY THING BACKING SHIELDED VALUE. `Hinkal.transact` computes `balanceDif = new - old (+ msg.value for address(0))` from `getBalancesForArray` and requires `balanceDif == (onChainCreation[i] ? 0 : amountChanges[i]) + utxoAmount`, where `utxoAmount` sums only `utxoSet` entries whose `erc20Address` matches. Probe every way the two sides agree while the vault is short: a token whose `balanceOf` the caller steers between the two snapshots, address(0) listed alongside its wrapper so one ETH movement satisfies two legs, a rebasing or fee-on-transfer token, `onChainCreation` switching the RHS to zero, and `int256` casts of balances near 2**255. Identity: net value entering Hinkal == sum of `amountChanges` + sum of on-chain UTXO amounts inserted as leaves.",

    "Critical. ETH IS COUNTED FOUR DIFFERENT WAYS. `transact` adds `msg.value` to `balanceDif` only when address(0) is listed and `oldBalances` already contains it; `_internalTransact` requires `msg.value == amountChanges[i]` per ETH leg via `transferERC20TokenFromOrCheckETH`; `prooflessDeposit` subtracts `msg.value` from `balanceBefore` once per unique token; `HinkalWrapper._settleFee` forwards `msg.value - feeAmount`; `DepositOnChainUtxosExternalAction` skips the transfer for address(0) and relies on Hinkal's equation; Emporium ops spend `op.value` from Emporium's balance and `handleOut` sends ETH back through `receive()`. Find a combination - ETH listed with `onChainCreation`, ETH not listed while msg.value is sent, ETH returned by an action in the same tx as msg.value - where one wei of ETH is credited to two accounting terms or credited without arriving. Identity: ETH credited as shielded or on-chain UTXO value == ETH that arrived at Hinkal in that transaction.",

    "Critical. TRUST IN `onlyAllowedRecipient` IS TRANSITIVE. `ExternalActionBaseV2` / `ExternalActionBaseUpgradeable` admit every address in `isAllowedRecipient`, and the comment says it serves 'VolatileTokenAction and Hinkal interactions', so Hinkal is not the only caller. If Emporium (or any action) is an allowed recipient of `DepositOnChainUtxosExternalAction`, a stateless Emporium op can call its `runAction` with a fabricated `circomData.originalSender` equal to any victim holding a standing allowance, pulling the victim's tokens to `msg.sender` (Emporium); `handleOut` then credits that gain to the attacker's own `stealthAddressStructure`. The same op can drive `LifiExternalAction.runAction` to swap the action's residual balance to Emporium. Map the full caller graph of `runAction` implementations and show the shortest unprivileged path from an Emporium op to a `transferFrom` or `transfer` on someone else's value. Identity: `msg.sender` of every `runAction` == Hinkal, and `originalSender` == the EOA that submitted the proof.",

    "Critical. STANDING APPROVALS TO THE DEPOSIT ACTION ARE SPENT ON `originalSender`'S BEHALF. `DepositOnChainUtxosExternalAction.runAction` calls `transferERC20TokenFrom(token, circomData.originalSender, msg.sender, tokenTotal)`; the only binding of `originalSender` to the real submitter is `HinkalHelper.performHinkalChecks` (`originalSender == sender && relay == 0`), enforced in a swappable helper and never re-checked in the action; for address(0) the action pulls nothing and relies on Hinkal's msg.value equation, and `deltaAmounts[i] == 0` is required while `utxoAmounts` metadata decides what is minted. Show a path where the address whose allowance is consumed is not the address that produced the proof, where the UTXO count from `countUtxos` and the amounts pulled diverge, or where an ETH UTXO is credited without msg.value backing it. Identity: `from` in every `transferFrom` issued by the action == `msg.sender` of the `Hinkal.transact` that carried the proof, and sum of minted UTXO amounts == tokens pulled.",

    "Critical. ZERO MEANS FIVE DIFFERENT THINGS. `insertCommitments` skips leaves equal to 0; `insertNullifiers` skips nullifiers equal to 0; `NullifierCalculator` and `OriginalCommitmentCalculator` output 0 when the commitment or amount is 0; `MerkleRootCalculator` treats a sibling of 0 as 'stop here'; `rootHashExists` returns `_root == 0` on an empty tree and rejects `_root == 0` otherwise; `ForceEqualIfEnabled(enabled = inAmounts)` disables the root check at amount 0; on-chain padding hashes `hash2(node, 0)`. Find a value that one component produces as a legitimate zero and another interprets as 'absent': an on-chain UTXO with amount 0 from an action, a nullifier that is 0 for a value-bearing leaf, a leaf whose sibling is a genuine zero-valued node, a fresh deployment whose first proof cites root 0. Identity: a zero produced by any component == a zero every consumer of that value treats as absent.",

    "Critical. THE TREE AND THE CIRCUIT MUST AGREE ON WHICH (LEAF, ROOT) PAIRS EXIST. `Merkle.insertMany` keeps one frontier node per level in `tree[]`, computes `twoPower = ceil(log2(fullCount))` from the FINAL count of the batch and stores `roots[newIndex-1] = tree[twoPower]` - so the first leaf is literally its own root and roots live at growing depths. `sortInPairs` / `insertTwo` skip writing `tree[0]` for paired leaves; `insertOne` treats `currentNodeIndex == 1` as left. `MerkleRootCalculator` keeps hashing through zero siblings but selects the root as the value after the LAST non-zero sibling. Show a path the circuit accepts for a leaf never inserted under that root, a batch boundary where `tree[i]` holds a stale node that a later right-child insertion reads, or a root stored under an index that `rootHashExists` maps to a different tree state. Identity: {(leaf, root) accepted by the circuit} == {(leaf, root) produced by `insert*` and stored in `roots`}.",

    "Critical. ONE LEAF, ONE NULLIFIER, ONE SPEND. Commitment = `Poseidon4(amount, token, stealthAddress, timeStamp)` and nullifier = `Poseidon2(commitment, Poseidon2(nullifyingPrivateKey, commitment))`, so identical preimages share one nullifier and the second leaf is dead the moment the first is spent. `DepositOnChainUtxosExternalAction` stamps `circomData.timeStamp + utxoIndex`, `EmporiumUpgradeable.handleOut` stamps `circomData.timeStamp`, `prooflessDeposit` stamps `block.timestamp`, and on-chain UTXOs are emitted in full inside `NewCommitment`, so every preimage is public. Show a sequence where an unprivileged caller makes a victim's value-bearing leaf unspendable (permanent freeze), or where the same nullifier value is accepted twice through the `onChainCreation` break in `insertNullifiers`, the zero skip, or two Hinkal instances. Identity: spendable leaves carrying value == distinct nullifiers that will ever be accepted for them.",

    "Critical. NOTHING SEPARATES DEPLOYMENTS EXCEPT `block.chainid`. Hinkal is live on Ethereum, Arbitrum, Optimism, Base and Polygon; `HinkalFactoryDeployer` uses `SAFE_SINGLETON_FACTORY` with the fixed salt `keccak256(\"HINKAL\")` so factories and therefore Hinkal addresses repeat across chains; `getSignedMessageHash` mixes in `block.chainid` and `hinkalAddress`, but commitments, nullifiers, stealth addresses, `emporiumMessage`, `usedMessages` and EIP-712 stacks (domain `Emporium/1.0.0`) carry only what their own domain adds. Show a proof, nullifier, on-chain UTXO preimage, wallet stack or cancel signature produced for one chain or one Hinkal/Emporium instance that is accepted by another, or a same-chain redeploy through `HinkalFactory.deployHinkal` where leaves re-imported into a new tree can be spent against both instances. Identity: every accepted artifact (proof, nullifier, message, signature) is valid for exactly one (chain, contract) pair.",

    "Critical. THE PROOF COVERS ONLY WHAT `formBasicInput` AND THE TWO HASHES SAY IT COVERS. `getHashedCalldata` hashes publicSignalCount, relay, emporiumMessage, externalActionData, slippageValues, hookData, encryptedOutputs, onChainEncryptedOutput, feeStructure, onChainCreation, originalSender, extraData; `getSignedMessageHash` adds root, tokens, amounts, timeStamp, nullifiers, outCommitments, calldataHash and the H0/H1 points; `buildVerifierId` derives the verifier from `Dimensions` and `externalActionId`; each `VerifierEVM*` wrapper checks only `input.length == inputAmount`. Find a field the contracts act on that is outside both hashes (`rootHashHinkalIndex`, `dimensions`, the a/b/c encoding), a `publicSignalCount` / `Dimensions` pair that maps calldata to a verifier whose circuit signal order differs from the vector built on-chain, or a Min-vs-normal selection that checks the proof against the wrong circuit. Identity: every value the chain acts on == the value the selected circuit constrained at the same public-signal index.",

    "Critical. TWO NUMBER SYSTEMS, ONE STORAGE. Public inputs are reduced mod `CIRCOM_P` only where the contracts remember to (`calldataHash`, `signedMessageHash`, negative `amountChanges`), while `nullifiers`, `roots`, `usedMessages`, `emporiumMessage`, `timeStamp`, `outCommitments` and stealth points are stored and compared as raw `uint256`; the generated verifier's field check is the only barrier to a value `x + P` aliasing `x`. `CircomDataBuilder.MAX_AMOUNT = 2**252` bounds `amountChanges` while `OverflowPreventer` bounds each amount by `(2**252 - 1) / nCount`; `Emporium op.value` is `uint128`, loop counters in `CircomDataBuilder` are `uint16`, and `getBalancesForArray` results are cast to `int256`. Show an input that is accepted by the verifier or a wrapper under one representation and matched on-chain under another - a nullifier stored as `x` but later presented as `x + P`, an amount that satisfies the circuit sum in the field but not as an integer, a truncated counter that silently drops public signals. Identity: the integer the contracts store or compare == the field element the circuit constrained.",

    "Critical. THE ACTION'S RETURN VALUE IS TRUSTED FOR EVERYTHING BUT THE SUM. `Hinkal.transact` sizes `onChainCommitments` as `utxoSet.length`, fills only entries whose `erc20Address` matches a listed token, and passes the whole array to `insertCommitments`, which adds `onChainCommitments.length` to the leaf count without checking `commitment != 0`; the UTXO's `amount`, `erc20Address` and `timeStamp` come from the action, only `stealthAddressStructure` is proof-bound, and `createOnchainCommitment` hashes with a single shared `onChainEncryptedOutput`. `EmporiumUpgradeable` shrinks `utxoSet` with `UTXOLib.skipLast` in assembly. Show an action output (a UTXO for an unlisted token, a zero-amount UTXO, a mis-sized `utxoSet`, an `onChainCreation[i]` leg that still returns a UTXO) that inserts a zero or duplicate leaf, credits value under the wrong token, or desynchronises `leaves`, `insertedIndexes` and the `NewCommitment` events. Identity: every leaf inserted == one value-bearing UTXO whose amount was counted in `balanceDif` for its own token.",

    "Critical. `prooflessDeposit` IS A MINT WITH NO PROOF. `Hinkal.prooflessDeposit` and `HinkalWrapper.prooflessDeposit` create on-chain UTXOs guarded only by `performProoflessDepositChecks` (equal lengths, `<= MAX_LEAVES_PD`, non-empty encrypted output, `amounts[i] > 0`) and the per-unique-token require `balanceAfter - balanceBefore == amount`; the caller chooses every field of `stealthAddressStructures`, `createBlockedUtxos` is only an event, and `HinkalWrapper._settleFee` pays a caller-chosen `feeRecipient` in a caller-chosen `feeToken` BEFORE `_pullAndApproveDepositTokens`, with no reentrancy guard on the wrapper. Show a deposit whose minted leaves exceed the value that arrived (a token whose `balanceOf` moves during the hook, duplicate tokens whose aggregation differs between `_calcTokenChangesForProoflessDeposit` and `_pullAndApproveDepositTokens`, a `feeRecipient` that re-enters the wrapper while its approvals to Hinkal are live). Identity: sum of on-chain UTXO amounts minted == net value transferred into Hinkal from the caller.",

    "Critical. STATELESS OPS LEAVE THEIR STATE IN EMPORIUM. Emporium is a `Transferer`, so it implements `onERC721Received` / `onERC1155Received` and accepts anything; every CASE 2 op runs with Emporium as `msg.sender`, so an LP position, a vault share, an NFT, a locked stake, a limit order, a permit2 allowance or a protocol-side balance created by a user's stateless op is owned by Emporium, not by the user's stealth address or `HinkalWallet`. Nothing in `runAction` forces a user to route stateful calls through `invokeWallet`, and the balance loop only sees ERC20/ETH balances of listed tokens. Show that a position a victim created through stateless ops (or a refund that arrives at Emporium after the victim's tx) is claimable by the next unprivileged caller through the Min circuit or a normal Emporium transaction. Identity: every asset or claim created by a user's ops is owned by that user's wallet or stealth address, never by Emporium.",

    "Critical. THE WALLET OWNER SIGNS LESS THAN WHAT EXECUTES. `EmporiumUpgradeable.verifyWallet` covers only `(emporiumMessage, ops, maxFee, deadline)`; `feeStructure.feeToken`, `relay`, `erc20TokenAddresses`, `deltaAmountChanges` and the output `stealthAddressStructure` are bound only through the ZK proof's `calldataHash`, and the secrecy of `messageSeed` is the sole reason a harvested stack cannot be re-executed under an attacker's `CircomData`. `usedMessages` is written BEFORE the signature is checked; `cancelEmporiumMessage` accepts any signer who is `msg.sender`; `HinkalWallet` is designed for EIP-7702 delegation, so `callHinkalWallet` exposes the delegating EOA's entire balance and allowances to whatever ops Emporium forwards. Show a signed stack, a dropped or reverted mempool transaction, a Min-circuit proof for the same message, or an op whose `bytes4(op.callData)` dodges the two-selector filter, that moves wallet or EOA assets to a destination the owner never signed. Identity: (assets leaving the wallet, their destination) == (ops, maxFee) the wallet owner signed.",

    "Critical. HOOKS AND RECIPIENTS GET CONTROL WITH HINKAL AS `msg.sender`. `Hinkal.transact` calls `preHookContract.preTransact(circomData)` before the balance snapshot and `postHookContract.afterTransact(circomData)` AFTER the balance equation passes but BEFORE `insertNullifiers` / `insertCommitments`; `_internalTransact` sends ETH to a caller-chosen `externalAddress` via `transferETH`; ERC777 and callback tokens hand control to the attacker inside `getBalancesForArray`'s window. Hinkal is the trusted `msg.sender` for `onlyHinkal` in HinkalHelper and `onlyAllowedRecipient` in every external action, `nonReentrant` guards only `transact` and `prooflessDeposit`, and `HinkalWrapper` has no guard at all. Show a hook, recipient or token callback that changes a balance, allowance, action state or wrapper approval between the equality check and the leaf/nullifier writes, or reaches a Hinkal-trusting function through Hinkal's identity. Identity: the state the balance equation checked == the state that exists when nullifiers and commitments are written.",

    "Critical. THE HELPER IS THE ONLY PLACE ANYTHING IS CHECKED, AND IT IS A VIEW ON A MUTABLE ADDRESS. `HinkalHelper.performHinkalChecks` alone enforces `originalSender`/`relay` pairing, `relayerIsValid` (`tx.origin == relay`), `dimensionsCheck`, `checkOnchainCreation` and the calldata-hash integrity, and it builds the verifier input with `hinkalAddress` as `verifyingContract`; Hinkal calls it through a `hinkalHelper` storage pointer and then trusts every downstream contract to have been protected by it. `dimensionsCheck` compares inner lengths only against index 0, `checkOnchainCreation` inspects `inputNullifiers` but not `outCommitments`, `feeStructure.variableRate == 10000` sends 100% of a withdrawal to the relay, and nothing bounds `timeStamp`. Show an input shape or relay/sender combination that passes every helper check yet reaches `_internalTransact`, an external action or `insertCommitments` with a meaning the checks did not cover - a relayed transaction paying nothing, an `originalSender` that is a contract acting for someone else, arrays whose later rows differ from row 0. Identity: the CircomData shape and roles the helper validated == the shape and roles every downstream consumer assumes.",

    "Critical. THE MISSING INVARIANT - what nobody built. No contract asserts that Emporium, LifiExternalAction or DepositOnChainUtxosExternalAction hold zero balance, zero positions and zero outstanding approvals between transactions, yet every accounting rule assumes it; no on-chain check ties `publicSignalCount` or the order of `formBasicInput` to the public-signal layout of the verifier that `buildVerifierId` selects; commitments and nullifiers are domain-separated by nothing while addresses repeat across five chains; `transact` accepts any historical root forever and never checks `timeStamp` against `block.timestamp` outside the LiFi window; hook contracts and `feeRecipient` run with no whitelist; on-chain UTXO preimages are public and their timestamps caller-chosen. Identify the FIRST point at which one of these unstated assumptions is violated by an unprivileged caller with only their own funds and their own proof, prove it with a Foundry/Hardhat test that asserts vault balance versus total shielded value before and after, and show that once the two diverge nothing in the protocol can detect or reverse it.",
]


scope_scan = [
]


def question_generator(target_file: str) -> str:
    """
    Generate value-conservation audit questions for one Hinkal target.

    ```
    target_file format:
    "'File Name: contracts/Hinkal.sol -> Scope: Critical. ...'"
    """

    prompt = f"""
    ```

    Generate smart-contract and zk-circuit security audit questions for this exact Hinkal
    target:

    {target_file}

    Project focus:
    Hinkal is a shielded-UTXO pool on EVM chains. Untrusted bytes enter through two doors:
    `Hinkal.transact(a, b, c, dimensions, circomData)` and `Hinkal.prooflessDeposit(...)`
    (also via `HinkalWrapper`). From those bytes the contracts decide (a) what the Groth16
    proof constrained - `CircomDataBuilder` builds `calldataHash`, `signedMessageHash` and the
    public-input vector, `VerifierFacade` picks the verifier from `Dimensions`; (b) whether
    value is conserved - `balanceDif == amountChanges + utxoAmount` after an internal
    transfer or an external action (`EmporiumUpgradeable`, `LifiExternalAction`,
    `DepositOnChainUtxosExternalAction`) that runs caller-supplied metadata; (c) whether a
    leaf is spent once - `nullifiers` mapping, `Merkle` roots, `MerkleRootCalculator`'s
    zero-sibling truncation. Anything acted on but not constrained by the proof, or moved but
    not counted in the balance equation, is the bug.

    Rules:
    * Treat `File Name:` as the exact file.
    * Treat `Scope:` as the ONLY impact to target.
    * Assume full repo context is accessible.
    * Do not ask for code or say anything is missing.
    * Use exact Solidity/Circom symbols (contract, function, modifier, struct field, signal,
      template, constant) as they appear in the file.
    * EVERY question must close on an equality that must hold across a call. State it
      explicitly. Narrative questions with no stated equality are rejected.
    * Attacker is unprivileged only: any EOA on the chain. They may deposit their own funds,
      generate their own valid proofs for their own UTXOs, deploy contracts (hooks, fake
      tokens, endpoints, recipients), craft every field of `CircomData`, `Dimensions`,
      `externalActionMetadata` and deposit arrays, choose gas and ordering, and use public
      flash liquidity.
    * Attacker is NOT the owner, DEFAULT_ADMIN_ROLE, HINKAL_HELPER_MANAGER, a whitelisted
      relay, the factory owner, an upgrade admin, or the victim. They hold no private key of
      another user, no nullifyingPrivateKey but their own, and no trusted-setup toxic waste.
      No malicious relayer, sequencer, node or RPC; no compromised dependency; no social
      engineering.
    * PROGRAM EXCLUSIONS - a question landing in any of these wastes the whole batch:
      - contracts/verifiers/**, contracts/types/IVerifierEVM*.sol and
        circuits/BabyJubjubConstants.circom are generated and OUT OF SCOPE, as are README,
        tests, mocks, scripts and config.
      - Denial of service, gas griefing, block stuffing, front-running that only reverts a
        victim's transaction, unbounded loops, storage growth and memory hygiene are OUT OF
        SCOPE.
      - Defects inside Poseidon, circomlib, snarkJS, OpenZeppelin or the LI.FI router with no
        exploit path through this repository's own code are OUT OF SCOPE; a weakness here
        that steers them into unsafe behaviour is fully IN scope.
      - Also excluded: leaked keys, privileged accounts, centralization risk, best-practice
        notes, feature requests, price-oracle or depeg assumptions, funds sent to a contract
        by user mistake, and theoretical findings with no demonstration.
    * IN-SCOPE IMPACTS - every question must land on one and name it:
      Critical: direct theft of shielded or in-flight user funds; minting shielded value
      without backing or spending a leaf twice (protocol insolvency); permanent freezing of
      user funds; proof or nullifier verification bypass.
      High: theft or permanent freezing of protocol/relay fees; temporary freezing of user
      funds; executing calls or moving assets a wallet owner or prover never authorised.
    * Every question must be a concrete real-world scenario an unprivileged EOA can execute
      against the deployed contracts through `transact`, `prooflessDeposit` or
      `HinkalWrapper.prooflessDeposit`, with their own funds and their own proof.
    * A revert is a finding only when it permanently strands value or lets an unproven value
      through - say which.
    * Generate 40 to 80 high-signal questions.
    * At least 70% must land on a Critical impact rather than a High one.
    * Every question must be testable in a Foundry or Hardhat test on a local fork with
      locally generated snarkjs proofs. Never propose testing on mainnet or a public testnet.
    * Avoid generic checklist questions and repeated root causes.
    * Prefer questions that name TWO values that must be equal and ask whether they are: a
      field acted on and a field hashed into the proof, value moved and value counted, a
      root the circuit derives and a root the tree stored, a leaf inserted and a nullifier
      accepted, tokens leaving an action and tokens Hinkal sent it.

    Known dead ends - do NOT generate questions about these:
    * Anything needing an owner, admin, relay or manager key, or another user's keys.
    * A CVE in a dependency with no reachable path through this repo.
    * Findings only reproducible in generated verifiers or against a hypothetical misuse by
      the Hinkal frontend.
    * Timing, DoS, gas, or a user harming only their own shielded balance with no protocol or
      third-party loss.

    Core equalities (each question must close on one):
    * PROOF COVERAGE: every `CircomData` field acted on is inside `calldataHash`,
      `signedMessageHash` or the public-input vector at the index the circuit expects.
    * VALUE CONSERVATION: net tokens entering Hinkal == sum of `amountChanges` + amounts of
      on-chain UTXOs inserted; tokens leaving an action == `-deltaAmountChanges` it received.
    * TREE TRUTH: the (leaf, root) pairs `MerkleRootCalculator` accepts == the pairs
      `Merkle.insert*` produced and stored in `roots`.
    * SINGLE SPEND: one value-bearing leaf == one nullifier ever accepted for it.
    * AUTHORITY: `from` of every transferFrom, and every op executed against a wallet, was
      authorised by the account that produced the proof or the signature.

    Each question must include:
    1. target contract/function or template/signal;
    2. attacker action (a concrete call with the CircomData / metadata fields that matter);
    3. preconditions (tree state, registered actions, balances, approvals);
    4. call sequence through the contracts and circuit;
    5. the equality that breaks, written explicitly;
    6. scoped impact and whose funds or fees are exposed;
    7. proof idea.

    Output only valid Python. No markdown. No explanations.

    questions = [
    "[File: {target_file}] [Method: contract_or_function] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS trigger CALL_SEQUENCE, breaking the equality EQUALITY, causing scoped impact: SCOPE_IMPACT against PARTY? Proof idea: Foundry/Hardhat fork test PARAMETERS asserting PROOF_COVERAGE, VALUE_CONSERVATION, TREE_TRUTH, SINGLE_SPEND, or AUTHORITY.",
    ]
    """
    return prompt


def audit_format(security_question: str) -> str:
    """
    Generate a value-conservation Hinkal exploit-validation prompt.
    """

    prompt = f"""# SECURITY AUDIT PROMPT

## Question
{security_question}

## Rules
- Use existing repo context only. Analyze only this question and scoped impact.
- Attacker is unprivileged only: any EOA who can deposit their own funds, generate proofs for their own UTXOs, deploy contracts (hooks, tokens, endpoints), craft every field of `CircomData`, `Dimensions`, `externalActionMetadata` and deposit arrays, and choose ordering. They are not the owner, DEFAULT_ADMIN_ROLE, HINKAL_HELPER_MANAGER, a whitelisted relay, an upgrade admin or the victim, and hold no other user's keys.
- Reject malicious relayer/node/RPC assumptions, compromised dependencies, social engineering, and any path requiring a privileged role.
- OUT OF SCOPE, reject on sight: `contracts/verifiers/**`, `contracts/types/IVerifierEVM*.sol`, `circuits/BabyJubjubConstants.circom` (generated), README, tests, mocks, scripts, config; denial of service, gas griefing, revert-only front-running, unbounded loops and memory hygiene; Poseidon, circomlib, snarkJS, OpenZeppelin or LI.FI router defects with no exploit path through this repo's code; price-oracle or depeg assumptions; funds sent by user mistake; best-practice notes; theoretical findings.
- The impact must be one of: Critical - direct theft of shielded or in-flight user funds, minting shielded value without backing or double spend, permanent freezing of user funds, proof or nullifier verification bypass; High - theft or permanent freezing of protocol/relay fees, temporary freezing of user funds, executing calls or moving assets a wallet owner or prover never authorised.
- Focus on real impact: value leaving Hinkal or an action that was not counted, a leaf spent twice or stranded, or a field acted on that the proof never constrained.

## Validate
- Write the equality the question claims is broken between two named values BEFORE tracing any code.
- Trace the exact reachable path from the attacker's call and record every read and write of `amountChanges`, `deltaAmountChanges`, `balanceDif`, `utxoAmount`, `msg.value`, `nullifiers`, `roots`, `tree`, `m_index`, `usedMessages`, `calldataHash`, `signedMessageHash`, the public-input vector and the circuit signals it maps to.
- Evaluate both sides of the equality before and after. If they still match, output no vulnerability.
- Check whether `performHinkalChecks` (originalSender/relay, `dimensionsCheck`, `checkOnchainCreation`), `verifyProof` and `buildVerifierId`, `rootHashExists`, the balance and slippage requires, `insertNullifiers`, `onlyAllowedRecipient`, `verifyWallet`, `nonReentrant`, or the circuit constraints (`inTotal + amountChanges === outTotal`, `OverflowPreventer`, `BabyJubjubSubgroupCheck`, `ForceEqualIfEnabled`) already prevent the divergence.
- State what the attacker gains per transaction and whether it is repeatable.
- Require exact file/function support and a reproducible Foundry or Hardhat fork test with locally generated proofs.

## Output
If valid, output exactly:

### Title
[Bug statement] - ([File: file_path])

### Summary
[2-3 sentences]

### Finding Description
[The broken equality, the code path, root cause, the attacker's exact call, exploit flow, and why existing guards fail]

### Impact Explanation
[What is stolen, minted, frozen or bypassed, which party, repeatability, matching severity category]

### Likelihood Explanation
[Preconditions, tree/action state required, attacker cost, feasibility, repeatability]

### Recommendation
[Specific fix]

### Proof of Concept
[Foundry/Hardhat test plan with the exact assertions on both sides of the equality]

If invalid, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def validation_format(report: str) -> str:
    """
    Generate a strict bounty-style validation prompt for Hinkal claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- Check SECURITY.md and Researcher.Md for scope, exclusions, and valid impact classes.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the provided evidence proves the higher impact.
- A claim is only valid if the report states the broken equality between two named values and shows both sides concretely. Reject prose-only claims.
- Reject anything requiring the owner, DEFAULT_ADMIN_ROLE, HINKAL_HELPER_MANAGER, a whitelisted relay, an upgrade admin, another user's keys, a malicious relayer/node/RPC, a compromised dependency, or social engineering.
- OUT OF SCOPE, reject on sight: `contracts/verifiers/**`, `contracts/types/IVerifierEVM*.sol`, `circuits/BabyJubjubConstants.circom` (generated), README, tests, mocks, scripts, config; denial of service, gas griefing, revert-only front-running, unbounded loops and memory hygiene; Poseidon, circomlib, snarkJS, OpenZeppelin or LI.FI router defects with no exploit path through this repo's code; price-oracle or depeg assumptions; centralization risk; funds sent by user mistake; best-practice notes; feature requests; theoretical findings.
- The impact must be one of: Critical - direct theft of shielded or in-flight user funds, minting shielded value without backing or double spend, permanent freezing of user funds, proof or nullifier verification bypass; High - theft or permanent freezing of protocol/relay fees, temporary freezing of user funds, executing calls or moving assets a wallet owner or prover never authorised.
- Reject claims where the only loss is the attacker's own shielded balance.
- Reject if the bug was already fixed, publicly disclosed, or covered by a known-issues list.
- A valid report must be triggerable by an unprivileged EOA against the current contracts with their own funds and proof.
- A PoC is mandatory. Prefer #NoVulnerability over speculative reports.

## Required Validation Checks
All must pass:
1. Exact in-scope file, contract/function or template/signal, and line references.
2. The equality written explicitly, with both sides shown before and after.
3. Clear root cause: which unconstrained field, uncounted transfer, tree/circuit divergence, reusable nullifier, or missing check causes it.
4. Reachable exploit path: preconditions -> attacker call -> contract and circuit sequence -> observed divergence.
5. `performHinkalChecks`, `verifyProof`, `rootHashExists`, the balance equation, `insertNullifiers`, `onlyAllowedRecipient`, `verifyWallet`, `nonReentrant` and the circuit constraints reviewed and shown insufficient.
6. Impact stated concretely: which funds or fees, whose, and whether it is repeatable.
7. Reproducible proof: Foundry or Hardhat fork test with locally generated proofs and the asserted values.

## Silent Triage Questions
Before output, internally answer:
- What exactly is the equality, and does it actually fail?
- Can an ordinary EOA trigger it with no privileged role and no other user's key?
- Is the flaw in this repo's contracts or circuits, not in a dependency or the frontend?
- What value is stolen, minted or frozen, whose is it, and can it be repeated?
- Would an Immunefi triager accept the exploit path under the smart-contract severity system?
- What exact test would prove it?

## Output
If valid, output exactly:

Audit Report

## Title
[Clear vulnerability statement] - ([File: file_path])

## Summary
[2-3 sentence summary of the broken equality and impact]

## Finding Description
[Exact code path, the equality, root cause, exploit flow, and why existing guards fail]

## Impact Explanation
[What is stolen, minted, frozen or bypassed, affected party, repeatability, severity category]

## Likelihood Explanation
[Attacker capability, preconditions, state required, cost, feasibility]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or Foundry/Hardhat test plan with concrete assertions]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt


def scan_format(report: str) -> str:
    """
    Generate a short cross-project analog scan prompt for Hinkal.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Rules
- Use in-scope repo context only (`contracts/**` and `circuits/**`, excluding `contracts/verifiers/**`, `contracts/types/IVerifierEVM*.sol` and `circuits/BabyJubjubConstants.circom`). Do not ask for code or claim missing files.
- Use the external report only as a bug-class hint, not as proof.
- Keep only unprivileged-EOA analogs that break an equality: a `CircomData` field acted on but outside `calldataHash` / `signedMessageHash` / the public-input vector, value moved by Hinkal or an external action but not counted in the balance equation, a (leaf, root) pair the circuit accepts that the tree never produced, a nullifier reusable or a value-bearing leaf left unspendable, or a transferFrom / wallet op not authorised by the prover or signer.
- OUT OF SCOPE, reject on sight: generated verifiers and constants, README, tests, mocks, scripts, config; denial of service, gas griefing, revert-only front-running, unbounded loops and memory hygiene; Poseidon, circomlib, snarkJS, OpenZeppelin or LI.FI router defects with no exploit path through this repo's code; anything requiring an owner, admin, relay, manager, upgrade key or another user's key; malicious relayer/node assumptions; price-oracle or depeg assumptions; funds sent by user mistake; best-practice notes; theoretical findings.
- The impact must be one of: Critical - direct theft of shielded or in-flight user funds, minting shielded value without backing or double spend, permanent freezing of user funds, proof or nullifier verification bypass; High - theft or permanent freezing of protocol/relay fees, temporary freezing of user funds, executing calls or moving assets a wallet owner or prover never authorised.
- Reject analogs where the only loss is the attacker's own shielded balance.

## Validate
- Map the bug class to the strongest reachable path in this repo and state the equality it would break.
- Evaluate both sides before and after the attacker's call sequence.
- Prove root cause with exact file/function or template/signal support.
- Accept only concrete theft, unbacked minting or double spend, permanent or temporary freezing, proof/nullifier bypass, or unauthorised asset movement.

## Output (Strict)
If valid analog exists, output:

### Title
[Clear vulnerability statement] - ([File: file_path])

### Summary
### Finding Description
### Impact Explanation
### Likelihood Explanation
### Recommendation
### Proof of Concept

If not, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt
