# [C] C-03 | gmxUnlockDate And glpUnlockData Should Be Updated On Every Deposit

## Summary
Severity: Critical
Contest weight: 0.4033
Dataset id: 2012
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the ExitVault contract, the variables gmxUnlockDate and glpUnlockDate are initialized only during the first deposit to mark the
end of one-year vesting period for the esGMX tokens. Specifically, they are set in the deposit function when these variables are
zero:
if (s.gmxUnlockDate = 0) {s.gmxUnlockDate = block.timestamp + SECONDS_IN_YEAR;
emit GMXVestingStarted(msg.sender, s.gmxUnlockDate);} if (s.glpUnlockDate = 0) {s.glpUnlockDate = block.timestamp +
SECONDS_IN_YEAR; emit GLPVestingStarted(msg.sender, s.glpUnlockDate);}
However, these unlock dates are not updated on subsequent deposits. This means that if additional deposits are made after the
initial deposit, the gmxUnlockDate and glpUnlockDate remain unchanged. As a result, the vault owner can call earlyOwnerExit
once the initial unlock dates have passed, even if not all esGMX tokens from the later deposits have been fully vested into
GMX. This allows the owner to exit earlier than expected before the vesting period for the new deposits is complete.
When the owner calls earlyOwnerExit, the vault withdraws all vested tokens and signals the transfer of the vault's account to a
specified receiver. However, during this process, the state variables gmxSupply and glpSupply are not updated to reflect the
withdrawal. These variables continue to represent the total supply as if the tokens were still in the vault.
As a consequence, the accumulated reward per share variables s.accumulatedGmxWethPerShare and
s.accumulatedGlpWethPerShare become inaccurate because they rely on gmxSupply and glpSupply for their calculations. When
users attempt to claim rewards or interact with the vault, the contract may attempt to distribute more WETH rewards than what it
actually possesses reverting due to insufficient balance.
This inconsistency in the vault's accounting can cause a Denial of Service for users, preventing them from withdrawing their funds
or claiming rewards. Finally, it should also be taken into consideration that the vault owner can use earlyOwnerExit to signal an
account transfer and move out all the GMX-related funds.
This is only possible if one year has passed the first user deposit. When the acceptTransfer is executed, it will unstake all
the user's funds from the vester contracts and transfer them to the receiver, receiving funds that belong to the depositors.

## Recommendation
To prevent the vault owner from exiting earlier than expected and to ensure that all users receive their intended GMX rewards, the
gmxUnlockDate and glpUnlockDate should be updated with each new deposit. On the other hand, in the earlyOwnerExit function,
update the gmxSupply and glpSupply variables to account for the tokens withdrawn during the exit.
Consider also designing a withdrawal system where only the owner's GMX tokens are transferred to receiver and the remaining
can be claimed by stakers, including rewards. Consider creating an escrow contract where the GMX and GLP from users are sent
during earlyOwnerExit to avoid being removed during the accountTransfer call by recipient.
