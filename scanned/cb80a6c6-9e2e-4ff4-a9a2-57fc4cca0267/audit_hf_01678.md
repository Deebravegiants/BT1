# [M] M-2 Insufﬁcient reentrancy protection in FluidVaultT1

## Summary
Severity: Medium
Contest weight: 0.2506
Dataset id: 9143
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Although the FluidVaultT1 smart contract code includes reentrancy protection, some functions remain unprotected:
• admin functions
• read-only functions
Admin functions Admin functions can be called by the DAO. Once the DAO proposal is approved, it can be executed by anyone. Here is a possible attack vector:
• An attacker calls operate().
• The attacker receives a call to their malicious smart contract from FluidVaultT1 while operate() is not ﬁnalized.
• The attacker's contract calls DAO.executeProposal() with, for example, an absorbDustDebt() call.
• The attacker allows the initial operate() to ﬁnish.
The issue is that operate() works with a copy of Variables.vaultVariables: • main.sol#L53 and stores them back at the end of the function: • main.sol#L553. Thus, any modiﬁcations to vaultVariables in absorbDustDebt() will be overwritten by the later update in operate(), as the copied memory value vaultVariables_ in operate() will remain unchanged after the update in absorbDustDebt(). Read-only functions The same vector applies here, but it affects the reading of certain variables like positionData and branchData, which undergo some modiﬁcations before the call to the malicious address. Vulnerabilities in this area typically appear in more complex smart contract integrations, for instance, when external protocols use read-only functions to integrate with Fluid. See an example at https://rekt.news/midas-capital-rekt/. Reentrancy spots The safeTransfer library only requires success on msg.value transfer without gas limitations. As a result, it is possible to receive a call to a malicious smart contract in the line: • safeTransfer.sol#L88. This function is used in the following lines: • main.sol#L515 • main.sol#L1122 • main.sol#L533-L540. Additionally, tokens with hooks (like ERC-777) can open up new spots for reentrancy during fund transfers from a user.

## Recommendation
We recommend:
• developing a dedicated function to verify the current reentrancy status, replacing repeated lines preceding key functions;
• implementing this function across all functions, including admin and read-only functions (e.g., fetchLatestPosition), provided it does not disrupt the contract's logic.
A perfect solution would be to have reentrancy protection at a higher Fluid level — on the Liquidity smart contract. This would also protect against cross-vault and cross-protocol reentrancies.
