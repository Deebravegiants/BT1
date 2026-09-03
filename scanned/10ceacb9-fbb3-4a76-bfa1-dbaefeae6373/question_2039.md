# Q2039: HinkalWallet control: call callHinkalWallet from a non-Emporiu [when the external action retur]

## Question
Can an unprivileged attacker call callHinkalWallet from a non-Emporium address after an implementation swap, where onlyEmporium binds to an immutable emporium set at construction, to drain the HinkalWallet's balance or make it approve/transfer to an attacker, specifically when the external action returns an empty UTXO set (where utxoAmount is zero while value still moved)?

## Target
- File/function: contracts/external-actions/emporium/HinkalWallet.sol :: callHinkalWallet / doSendToRelay / isValidSignature
- Entrypoint: Hinkal.transact (Emporium op)
- Attacker controls: Emporium op endpoint/value/callData, relay argument, signature bytes
- Exploit idea: abuse the wallet's forwarding under Emporium identity
- Invariant to test: only ops the wallet owner signed move the wallet's assets
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: fund a wallet, execute an op draining it, assert attacker gain
