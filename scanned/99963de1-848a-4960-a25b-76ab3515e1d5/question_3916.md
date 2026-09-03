# Q3916: relay/originalSender binding: make relayFee round to zero via variable [when amountChanges[i] is exact]

## Question
Can an unprivileged attacker make relayFee round to zero via variableRate/flatFee so hasPaidToRelay is true with no payment, where _internalTransact sets hasPaidToRelay even when relayFee is 0, to bypass the relay-payment invariant or spoof the sender identity that authorises deposits and transferFrom, specifically when amountChanges[i] is exactly zero for the affected token (where the zero branch skips value movement)?

## Target
- File/function: contracts/HinkalHelper.sol :: performHinkalChecks / relayerIsValid / Hinkal._internalTransact
- Entrypoint: Hinkal.transact
- Attacker controls: relay, originalSender, feeStructure
- Exploit idea: satisfy the relay/originalSender requires while evading payment or spoofing identity
- Invariant to test: relay==0 XOR relay paid, and originalSender == the funding account
- Expected Immunefi impact: High: theft or permanent freezing of protocol/relay fees
- Fast validation: Foundry: withdraw via relay path paying no fee, assert relay unpaid but tx succeeds
