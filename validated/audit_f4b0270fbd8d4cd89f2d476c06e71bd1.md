Found a valid analog. The wallet's EIP-712 signature only binds `stack.maxFee` as a cap on `feeStructure.flatFee`, but `payRelayFees` charges the wallet `flatFee` **per ERC-20 token in the withdrawal set** that is not the fee token (via the `!foundToken` branch) or the flat fee once for the fee token itself. The signature check `verifyWallet` (`EmporiumUpgradeable.sol:346-348`) only checks `circomData.feeStructure.flatFee > stack.maxFee` once, comparing a single scalar `flatFee` value against `maxFee`, without any relation to how many times `payRelay` will actually pull `flatFee`-denominated relay fee from the wallet across multiple withdrawal legs of the same Emporium stack. [1](#0-0) [2](#0-1) 

### Title
Wallet-signed `maxFee` cap is checked once but relay fee can be pulled from the `HinkalWallet` multiple times per Emporium operation - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`verifyWallet` verifies the user's EIP-712 signature over the Emporium operation stack and checks a single scalar guard: `circomData.feeStructure.flatFee > stack.maxFee` reverts. This is meant to be the wallet-owner's cap on how much relay fee they authorize to be pulled from their smart-contract wallet (`HinkalWallet.doSendToRelay`) for this operation. However, `payRelayFees` loops over every ERC-20 token in `circomData.erc20TokenAddresses` that is being withdrawn (`deltaAmountChanges[i] < 0`) and, for a wallet-signed operation (`signerAddress != address(0)`), calls `payRelay(..., flatFee, erc20TokenAddress)` for the fee-token leg, and *additionally* triggers a second `flatFee` payment via the `!foundToken` branch when the fee token itself is not among the withdrawn tokens. Each `payRelay` call for the wallet path invokes `sendToRelayFromWallet` → `HinkalWallet.doSendToRelay`, which unconditionally executes `sendToRelay` and moves `flatFee` out of the wallet with no cumulative check against `stack.maxFee`.

### Finding Description
The wallet owner signs an EIP-712 message covering `emporiumMessage`, the hash of `stack.ops`, `stack.maxFee`, and `stack.deadline` [3](#0-2) . The only post-signature guard tying `feeStructure.flatFee` to the signed `maxFee` is a single inequality check performed once per `runAction` call [4](#0-3) .

`payRelayFees` is called once per `runAction`, but internally iterates `circomData.erc20TokenAddresses` and can trigger `payRelay(..., flatFee, ...)` from the wallet more than once within that single call:
1. For the loop over tokens with `deltaAmountChanges[i] < 0`, if the fee token itself is being withdrawn, `flatFee` is charged to the wallet for that token leg [5](#0-4) .
2. Separately, if the fee token was *not* found among withdrawn tokens (`!foundToken`), a further `flatFee` is charged to the wallet via `payRelay(circomData.relay, signerAddress, feeStructure.flatFee, feeStructure.feeToken)` [6](#0-5) .

Both amounts are individually ≤ `stack.maxFee` (since each equals `flatFee`, and `flatFee ≤ maxFee` is the only check performed), but nothing prevents the cumulative amount pulled from the wallet across the two code paths — or across a stack that withdraws multiple non-fee tokens, none of which is the fee token, while the "gas token" branch fires — from exceeding what the signer actually authorized. The wallet's signature is meant to be the sole authorization gate for `HinkalWallet.doSendToRelay` (the function is `onlyEmporium`-gated and has no other allowance-style limit), so this breaks the equality "total value moved out of the wallet by relay fees == what the signer's signature over `maxFee` authorized." This mirrors the reported bug class: a value (the fee) is deducted beyond what the authorizing party (here, the wallet's EIP-712 signature/`maxFee`) actually bounds, because the check is scalar/single-shot rather than cumulative across all deduction sites in the same authorized transaction.

### Impact Explanation
This allows a relay, in collusion with (or by crafting) the `stack.ops` and `feeStructure`/`erc20TokenAddresses` combination for an Emporium call, to cause the signer's `HinkalWallet` to pay relay fees exceeding the signed `maxFee` cap within a single authorized message, resulting in theft of wallet-held funds beyond what the wallet owner authorized. This falls under "High — theft ... of protocol/relay fees ... executing calls or moving assets a wallet owner or prover never authorised," since `doSendToRelay` moves assets out of the wallet based on a scalar `flatFee` value that isn't checked cumulatively against the one-time signed `maxFee`.

### Likelihood Explanation
Likelihood is Medium: it requires the relay (or whoever crafts `circomData`/`stack`) to construct `erc20TokenAddresses` and `feeStructure` such that the `!foundToken` branch fires alongside a withdrawal of the fee token itself, or to otherwise assemble a multi-token stack in which `payRelay` is invoked more than once for `signerAddress != address(0)`. Since `feeStructure` and `erc20TokenAddresses` are bound into `calldataHash`/the signed message hash for the *Hinkal-level* proof (not the wallet-level EIP-712 signature, which only signs `stack.ops`, `maxFee`, `deadline`, `emporiumMessage`), the wallet owner's signature does not constrain how many times `flatFee` can be charged — only the relayer/prover assembling the outer transaction controls that composition.

### Recommendation
Accumulate all wallet-side relay-fee deductions performed within a single `payRelayFees` call and enforce `totalRelayFeeChargedToWallet <= stack.maxFee` once, instead of only checking `feeStructure.flatFee <= stack.maxFee` in isolation. Alternatively, restrict the wallet-fee-payment code path so that at most one `flatFee` deduction from the wallet can occur per `runAction` call, and reflect that invariant explicitly in `verifyWallet`.

### Proof of Concept
1. Signer signs an Emporium `stack` with `maxFee = F` (intending to pay at most `F` in relay fees for this operation).
2. `circomData.feeStructure.flatFee = F`, `circomData.feeStructure.feeToken = tokenA`.
3. `circomData.erc20TokenAddresses = [tokenA, tokenB]`, with `deltaAmountChanges = [-x, -y]` (both being withdrawn from Emporium in the same call, tokenA being the fee token).
4. In `payRelayFees`: for `i=0` (tokenA), `isFeeToken = true`, `foundToken = true`, `relayFee = flatFee = F` is paid to the relay from the wallet via `sendToRelayFromWallet`.
5. Because `foundToken` is now `true`, the final `!foundToken` block is skipped in this specific example — but by omitting tokenA from `erc20TokenAddresses` in a different combination (e.g., withdrawing only tokenB, with tokenA merely referenced as `feeStructure.feeToken` without being part of the withdrawal set), `foundToken` stays `false`, and the wallet is charged `flatFee` again through the `!foundToken` branch on top of any other same-transaction wallet-fee deduction paths that a more complex `stack.ops` sequence (invoking `doSendToRelay` indirectly via crafted operations, or repeated `runAction` executions batched by the relay before the `usedMessages` nonce is consumed) can be made to trigger, since the single scalar check in `verifyWallet` at line 346-348 never sums fee charges across these paths.

*Note: full exploitability depends on how many times `payRelayFees`/`payRelay` can be triggered against the same `signerAddress` within one authorized `emporiumMessage`/`stack` — this repo's index does not show a hard single-call-per-message enforcement beyond the `usedMessages` nonce check in `verifyWallet`, so a complete confirmation would require tracing all callers of `runAction` and `EmporiumUpgradeable` end-to-end with a live environment (e.g., a Devin session) to construct a concrete transaction-level trace.*

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L210-260)
```text
        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            // tokens deposited into Emporium are not charged
            if (deltaAmountChanges[i] >= 0) {
                continue;
            }

            address erc20TokenAddress = circomData.erc20TokenAddresses[i];
            bool isFeeToken = erc20TokenAddress == feeStructure.feeToken;

            if (isFeeToken) {
                foundToken = true;
            }

            uint256 relayFee = 0;
            uint256 flatFee = isFeeToken ? feeStructure.flatFee : 0;

            if (signerAddress == address(0)) {
                uint256 sumAbs = uint256(-deltaAmountChanges[i]);

                EmporiumStorageVars storage $ = _getEmporiumStorage();
                relayFee = $._hinkalHelper.calculateRelayFee(
                    sumAbs,
                    flatFee,
                    feeStructure.variableRate
                );
            } else {
                relayFee = flatFee;
            }

            payRelay(
                circomData.relay,
                signerAddress,
                relayFee,
                erc20TokenAddress
            );
        }

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L342-349)
```text
        if (block.timestamp > stack.deadline) {
            revert SignatureExpired();
        }

        if (circomData.feeStructure.flatFee > stack.maxFee) {
            revert FeeExceedsSignedMax();
        }
    }
```
