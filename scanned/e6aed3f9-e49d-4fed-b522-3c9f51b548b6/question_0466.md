# Q0466: relay/originalSender binding: set relay to a whitelisted relay while t [when a same-token second leg i]

## Question
Can an unprivileged attacker set relay to a whitelisted relay while tx.origin is the attacker to fail-open relayerIsValid, where relayerIsValid requires tx.origin == relay and isRelayInList, to bypass the relay-payment invariant or spoof the sender identity that authorises deposits and transferFrom, specifically when a same-token second leg is present in the same call (where the per-token loop processes that token twice)?

## Target
- File/function: contracts/HinkalHelper.sol :: performHinkalChecks / relayerIsValid / Hinkal._internalTransact
- Entrypoint: Hinkal.transact
- Attacker controls: relay, originalSender, feeStructure
- Exploit idea: satisfy the relay/originalSender requires while evading payment or spoofing identity
- Invariant to test: relay==0 XOR relay paid, and originalSender == the funding account
- Expected Immunefi impact: High: theft or permanent freezing of protocol/relay fees
- Fast validation: Foundry: withdraw via relay path paying no fee, assert relay unpaid but tx succeeds
