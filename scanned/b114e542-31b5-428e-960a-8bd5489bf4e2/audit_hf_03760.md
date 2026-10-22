# [H] Sybil on withdrawal requests can allow lever-

## Summary
Severity: High
Contest weight: 0.3287
Dataset id: 19927
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To be able to withdraw, a user has to request a withdraw first. The only requirement to be able to request a withdraw is to have a balance of SToken when requesting. By requesting withdraws with the same tokens but different addresses, a malicious user can create the option to withdraw during one cycle more than what is deposited in the protocol. They cannot drain the protocol since they only have a limited amount of SToken to burn (required to call withdraw()), but they acquire the ability to deposit new funds and withdraw them in the same block, thus manipulating premium prices. Consider the following scenario: A malicious user wants to manipulate leverageRatio (to get a cheaper premium for example). They deposit 10k USDC into the protocol, and get 10k STokens. They request immediately a withdraw, and transfer STokens to another address and request a withdraw there, repeating the process 10 times. This works since balance is checked on requesting withdrawal but not locked or time-locked. 2 cycles later (actually ~1 cycle if the timing is optimized), they have the ability to take a flashloan for 100k USDC, deposit through the 10 addresses used, enjoy the cheaper premium as a protection buyer due to leverageFactor being high and withdraw all in the same transaction. They can safely repay the flash loan. Protection buyers can use this to:
• game premium prices, meaning that protection sellers get rugged.
• overprotect their lending positions (used in conjunction with HIGH-02, it can drain the whole protection pool if lending pool defaults).
• DOS the protocol by sending the leverage factor very high.

## Recommendation
Freeze STokens for a depositor once they requested a withdrawal.
