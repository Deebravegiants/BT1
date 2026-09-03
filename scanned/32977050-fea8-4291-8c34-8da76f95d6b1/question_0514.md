# Q0514: HinkalWallet control: route value through doSendToRelay to an  [when a same-token second leg i]

## Question
Can an unprivileged attacker route value through doSendToRelay to an attacker-controlled relay, where doSendToRelay trusts the Emporium caller's relay argument, to drain the HinkalWallet's balance or make it approve/transfer to an attacker, specifically when a same-token second leg is present in the same call (where the per-token loop processes that token twice)?

## Target
- File/function: contracts/external-actions/emporium/HinkalWallet.sol :: callHinkalWallet / doSendToRelay / isValidSignature
- Entrypoint: Hinkal.transact (Emporium op)
- Attacker controls: Emporium op endpoint/value/callData, relay argument, signature bytes
- Exploit idea: abuse the wallet's forwarding under Emporium identity
- Invariant to test: only ops the wallet owner signed move the wallet's assets
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: fund a wallet, execute an op draining it, assert attacker gain
