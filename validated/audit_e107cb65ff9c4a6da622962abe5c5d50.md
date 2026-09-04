### Title
Emporium EIP-712 signature omits `feeToken` and `relay` from signed payload, letting anyone who obtains a valid `EmporiumStack` signature redirect wallet fees to an arbitrary token/destination while only the numeric `flatFee` is bound by `maxFee` - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`verifyWallet` only signs `emporiumMessage`, the hash of `ops`, `maxFee`, and `deadline`; it never binds `circomData.relay`, `circomData.feeStructure.feeToken`, or `circomData.feeStructure.variableRate` into the EIP-712 digest. Anyone who can present a validly-signed `EmporiumStack` (the caller assembling `CircomData` for `Hinkal.transact`, per the threat model) can therefore reuse that same signature with an attacker-chosen `relay` and an attacker-chosen `feeToken`, draining `flatFee` units of any ERC-20 the `HinkalWallet` happens to hold to an address the signer never authorised, all while satisfying the on-chain check `feeStructure.flatFee <= stack.maxFee`.

### Finding Description
The claimed invariant is: `(assets leaving the wallet, destination) == (ops, maxFee)` the owner signed via EIP-712.

In `verifyWallet` (contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:302-349), the signed digest is: [1](#0-0) 

only `emporiumMessage`, `_hashEmporiumOps(stack.ops)`, `stack.maxFee`, and `stack.deadline` are hashed. The only fee-related check performed afterward is: [2](#0-1) 

`circomData.relay`, `circomData.feeStructure.feeToken`, and `circomData.feeStructure.variableRate` are all read directly from the unsigned `CircomData` calldata that the caller of `runAction` (i.e., the tx submitter who assembled `circomData`) supplies, and are used unconditionally in `payRelayFees` (lines 201-260) and `payRelay`/`sendToRelayFromWallet` (lines 186-282) to move funds from the signer's `HinkalWallet`: [3](#0-2) 

When `feeStructure.feeToken` is not one of the tokens touched by the batch's `erc20TokenAddresses`/`deltaAmountChanges` (the "!foundToken" branch), the code still pulls `flatFee` of `feeStructure.feeToken` straight out of the signer's `HinkalWallet` via `sendToRelayFromWallet` → `IHinkalWallet.doSendToRelay` → `sendToRelay`, and pays it to `circomData.relay`. Neither `feeToken` nor `relay` were part of what the owner's signature covers - the signature only constrains the `ops` array (the wallet calls) and a numeric `maxFee` ceiling, with no token or recipient binding. `HinkalWallet.callHinkalWallet`/`doSendToRelay` (contracts/external-actions/emporium/HinkalWallet.sol:28-42) trust the `Emporium` contract unconditionally (`onlyEmporium`), so once `verifyWallet` passes, the wallet has no independent check on which token or which relay receives the fee.

Consequently, anyone in possession of a validly-signed `EmporiumStack` (obtainable from mempool/relay infrastructure, since the threat model explicitly allows the attacker to craft every field of `CircomData` and choose ordering/batching) can resubmit it through `Hinkal.transact` with:
- `circomData.relay` = attacker's own address (destination never signed).
- `circomData.feeStructure.feeToken` = any ERC-20 the victim's `HinkalWallet` holds, unrelated to the tokens actually moved by `ops` (token never signed).
- `circomData.feeStructure.flatFee` = any value `<= stack.maxFee` (only the number, not the unit/token, is bounded).

This passes `verifyWallet`'s signature and `flatFee <= maxFee` checks exactly as designed, yet moves an arbitrary token, to an arbitrary destination, out of the signer's wallet - a combination the owner's EIP-712 signature never constrained.

### Impact Explanation
This is theft of protocol/relay fees, and more importantly it is executing a fund transfer from the wallet owner's `HinkalWallet` that the owner's signature never authorised in terms of token and destination - matching the "High: executing calls or moving assets a wallet owner or prover never authorised" category. Because `feeToken`/`relay` are entirely free-form calldata fields checked against nothing but the token-agnostic numeric cap, an attacker who intercepts or is handed one valid signed `EmporiumStack` (e.g. from public relay infrastructure, which the protocol's own design assumes exists) can extract `flatFee` worth of any wallet-held token to themselves, repeatedly for every `emporiumMessage` nonce that is ever signed, until `usedMessages` marks that particular nonce spent (each valid signature can only be replayed once, but each such replay drains up to `maxFee` in a token/destination the owner never picked).

### Likelihood Explanation
Preconditions: a `HinkalWallet` owner must sign an `EmporiumStack` (any nonzero `maxFee`, e.g., a typical fee-relay signature) that is subsequently observable to a third party (relay infra, public tx pool, or any off-chain channel through which signed messages are routed to be executed) before being consumed. Given the protocol's design explicitly relies on a permissionless "relay" model (any `EmporiumUpgradeable`-recognized action passed through `Hinkal.transact`, gated only by `onlyAllowedRecipient` on the Hinkal contract itself, not on `circomData.relay`), it is reasonable to expect signed stacks are shared with third-party relayers, making interception plausible. Attacker cost is essentially zero once a signed message is obtained; the exploit requires no privileged role, only the ability to submit a transaction with attacker-chosen `circomData.relay`/`feeToken`/`flatFee`.

### Recommendation
Include `circomData.relay`, `feeStructure.feeToken`, and `feeStructure.variableRate` in the EIP-712 typed data hashed inside `verifyWallet`, so that the signer explicitly authorises the exact fee token, fee model, and relay destination, not merely a numeric ceiling on `flatFee`. Alternatively, restrict `circomData.relay` to a protocol-whitelisted set of relays and enforce that `feeStructure.feeToken` must be one of `circomData.erc20TokenAddresses` actually touched by the signed `ops`.

### Proof of Concept
Foundry test plan:
1. Deploy `EmporiumUpgradeable`, a `HinkalWallet` for a victim `signer`, fund the wallet with `TokenA` (used by `ops`) and `TokenB` (unrelated, high-value).
2. Have `signer` sign an `EmporiumStack{ops: [transfer TokenA], maxFee: 100, deadline: future}` bound to `emporiumMessage = 1`, with `feeToken` implicitly expected to be `TokenA` (as shown to the signer off-chain).
3. Attacker calls `Hinkal.transact` → `runAction` with the same signed `stack`, but `circomData.feeStructure = {feeToken: TokenB, flatFee: 100, variableRate: 0}` and `circomData.relay = attacker`.
4. Assert `verifyWallet` does not revert (signature still validates because `feeToken`/`relay` aren't hashed).
5. Assert `TokenB.balanceOf(attacker)` increased by 100 and `TokenB.balanceOf(wallet)` decreased by 100, even though `TokenB` was never referenced by `ops` and `attacker` was never named in the signed payload - i.e., assert `(assets leaving wallet, destination) != (ops, maxFee)` the owner signed, disproving the invariant.

### Citations

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
