# Q3214: HinkalWallet control: route value through doSendToRelay to an  [when the token silently return]

## Question
Can an unprivileged attacker route value through doSendToRelay to an attacker-controlled relay, where doSendToRelay trusts the Emporium caller's relay argument, to drain the HinkalWallet's balance or make it approve/transfer to an attacker, specifically when the token silently returns false on failure (where SafeERC20 and the balance delta can disagree)?

## Target
- File/function: contracts/external-actions/emporium/HinkalWallet.sol :: callHinkalWallet / doSendToRelay / isValidSignature
- Entrypoint: Hinkal.transact (Emporium op)
- Attacker controls: Emporium op endpoint/value/callData, relay argument, signature bytes
- Exploit idea: abuse the wallet's forwarding under Emporium identity
- Invariant to test: only ops the wallet owner signed move the wallet's assets
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: fund a wallet, execute an op draining it, assert attacker gain
