# Q2991: relay/originalSender binding: set originalSender==sender with relay==0 [when the token is a fee-on-tra]

## Question
Can an unprivileged attacker set originalSender==sender with relay==0 then have a hook set relay indirectly, where the originalSender/relay pairing is checked once up front, to bypass the relay-payment invariant or spoof the sender identity that authorises deposits and transferFrom, specifically when the token is a fee-on-transfer token (where delivered amount is below the stated amount)?

## Target
- File/function: contracts/HinkalHelper.sol :: performHinkalChecks / relayerIsValid / Hinkal._internalTransact
- Entrypoint: Hinkal.transact
- Attacker controls: relay, originalSender, feeStructure
- Exploit idea: satisfy the relay/originalSender requires while evading payment or spoofing identity
- Invariant to test: relay==0 XOR relay paid, and originalSender == the funding account
- Expected Immunefi impact: High: theft or permanent freezing of protocol/relay fees
- Fast validation: Foundry: withdraw via relay path paying no fee, assert relay unpaid but tx succeeds
