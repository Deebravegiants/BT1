# Q3032: LiFi swap: craft externalActionMetadata so the rout [when the token is a fee-on-tra]

## Question
Can an unprivileged attacker in a LiFi swap action craft externalActionMetadata so the router pays output to the attacker not the action, where getERC20OrETHBalance delta undercounts and Hinkal still credits a UTXO, to either steal the output/fees or make Hinkal credit a UTXO larger than the value the action actually delivered, specifically when the token is a fee-on-transfer token (where delivered amount is below the stated amount)?

## Target
- File/function: contracts/external-actions/swaps/LifiExternalAction.sol :: callRouter / ExternalActionSwap.swap
- Entrypoint: Hinkal.transact (LiFi action)
- Attacker controls: externalActionMetadata (router calldata), slippageValues, feeStructure, timeStamp, relay
- Exploit idea: decouple swappedAmount/fees from what the action forwards to Hinkal
- Invariant to test: amountToSendToHinkal == swappedAmount - totalFee and equals the credited UTXO
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry with a mock router: assert action residual or over-credit after swap
