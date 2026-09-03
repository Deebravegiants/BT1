# Q1889: HinkalWallet control: reach callHinkalWallet's endpoint.call w [at the maximum allowed array l]

## Question
Can an unprivileged attacker reach callHinkalWallet's endpoint.call with attacker calldata via an Emporium op, where the wallet forwards arbitrary endpoint/value/data under onlyEmporium, to drain the HinkalWallet's balance or make it approve/transfer to an attacker, specifically at the maximum allowed array lengths (where boundary sizing exposes off-by-one behaviour)?

## Target
- File/function: contracts/external-actions/emporium/HinkalWallet.sol :: callHinkalWallet / doSendToRelay / isValidSignature
- Entrypoint: Hinkal.transact (Emporium op)
- Attacker controls: Emporium op endpoint/value/callData, relay argument, signature bytes
- Exploit idea: abuse the wallet's forwarding under Emporium identity
- Invariant to test: only ops the wallet owner signed move the wallet's assets
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: fund a wallet, execute an op draining it, assert attacker gain
