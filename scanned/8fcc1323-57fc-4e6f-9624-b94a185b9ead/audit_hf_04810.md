# [M] L1 data fees are not reimbursed

## Summary
Severity: Medium
Contest weight: 0.4620
Dataset id: 22680
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
L1 data fees are not reimbursed, and they are often orders of magnitude more expensive than the L2 gas fees being reimbursed. Not reimbursing these fees will lead to jobs not being executed on L2s.
While the contest README says that the protocol is interested in all EVM-compatible chains, its not clear to what extent they need compatibility. For instance, many chains have workarounds for the fact that they need to publish data from the L2 to the L1 via calldata, and therefore charge for those operations directly. Such caveats indicate that the compatibility is not 100% and therefore we can't really assume that any random chain will be supported. However, the README explicitly mentions Optimism as a target chain, so its idiosyncracies are in-scope.
The Gelato protocol properly handles L1 data fees, but neither Keep3r nor OpenRelay do. It could be argued that for Keep3r, it's possible to modify a job's fee rate dynamically and therefore it's not that big a risk, but for OpenRelay, the reimbursement formula is hard-coded, which means there's no workaround.
Looking at a transaction from this vault, the transaction cost was 0.000305237594921218 ETH (1:17)butonly0:00000008929694256ETH(<0.01) was reimbursed. The L1 data fee was 0.000304676890061656 Eth, whereas the gas fee was 0.000000111805735391.
Ratio, and the L1 data fee is frequently much larger than the L2 gas fee, for extended periods of time. This essentially means that the protocol is broken on L2s for any use case which requires timely executions. The contest README states that the sponsor is interested in issues where future integrations would be negatively impacted, and one such case would be where an exchange is trying to use xkeeper above. Operations will appear to hang for multiple hours at a time, causing loss of funds for customers trying to close their orders.
Only the L2 gas is reimbursed, not any of the L1 data fees:
```solidity
// File: solidity/contracts/relays/OpenRelay.sol : OpenRelay.exec()
// Execute the automation vault counting the gas spent
uint256 _initialGas = gasleft();
_automationVault.exec(msg.sender, _execData, new IAutomationVault.FeeData[](0));
uint256 _gasSpent = _initialGas - gasleft();
// Calculate the payment for the relayer
uint256 _payment = (_gasSpent + GAS_BONUS) * block.basefee * GAS_MULTIPLIER / BASE;
// Send the payment to the relayer
IAutomationVault.FeeData[] memory _feeData = new IAutomationVault.FeeData[](1);
_feeData[0] = IAutomationVault.FeeData(_feeRecipient, _NATIVE_TOKEN, _payment);
39: _automationVault.exec(msg.sender, new IAutomationVault.ExecData[](0), _feeData);
```
ity/contracts/relays/OpenRelay.sol#L28-L39

## Recommendation
Every L2 has its own formula for calculating the L1 data fee, so different versions of the code will have to be written for each L2. This is the description for Optimism. those or these instructions.
