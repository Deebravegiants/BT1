# Q1591: relay/originalSender binding: set relay to a whitelisted relay while t [when the erc20TokenAddresses a]

## Question
Can an unprivileged attacker set relay to a whitelisted relay while tx.origin is the attacker to fail-open relayerIsValid, where relayerIsValid requires tx.origin == relay and isRelayInList, to bypass the relay-payment invariant or spoof the sender identity that authorises deposits and transferFrom, specifically when the erc20TokenAddresses array is reordered (where index-dependent loops behave differently)?

## Target
- File/function: contracts/HinkalHelper.sol :: performHinkalChecks / relayerIsValid / Hinkal._internalTransact
- Entrypoint: Hinkal.transact
- Attacker controls: relay, originalSender, feeStructure
- Exploit idea: satisfy the relay/originalSender requires while evading payment or spoofing identity
- Invariant to test: relay==0 XOR relay paid, and originalSender == the funding account
- Expected Immunefi impact: High: theft or permanent freezing of protocol/relay fees
- Fast validation: Foundry: withdraw via relay path paying no fee, assert relay unpaid but tx succeeds
