# Q5216: relay/originalSender binding: set originalSender==0 with relay!=0 but  [when the external action is Em]

## Question
Can an unprivileged attacker set originalSender==0 with relay!=0 but pay no relay fee via zero-fee feeStructure, where performHinkalChecks allows originalSender==0 only when relay!=0, to bypass the relay-payment invariant or spoof the sender identity that authorises deposits and transferFrom, specifically when the external action is Emporium with signerAddress zero (where the unsigned stateless op path runs)?

## Target
- File/function: contracts/HinkalHelper.sol :: performHinkalChecks / relayerIsValid / Hinkal._internalTransact
- Entrypoint: Hinkal.transact
- Attacker controls: relay, originalSender, feeStructure
- Exploit idea: satisfy the relay/originalSender requires while evading payment or spoofing identity
- Invariant to test: relay==0 XOR relay paid, and originalSender == the funding account
- Expected Immunefi impact: High: theft or permanent freezing of protocol/relay fees
- Fast validation: Foundry: withdraw via relay path paying no fee, assert relay unpaid but tx succeeds
