# [C] C-05 | Faulty ownerDeposit Mechanism

## Summary
Severity: Critical
Contest weight: 0.3979
Dataset id: 2014
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function ownerDeposit and its implementation brings many problems for the system. It creates several
issues for both sides of the vault. Firstly and most critical issue is: "Double Counting ownerInitialGMX
and ownerInitialGLP in ownerDeposit". During vault initialization, ownerInitialGMX and ownerInitialGLP
variables are initialized with the comment: “Store the total balance so that we know how much to transfer
back to the owner after a year exits.”
Which means owner will be able to withdraw this amount after the end of vesting. However in the
function ownerDeposit these values are incremented regardless if owner makes a new deposit or not.
Hence the initial amounts that are transferred via full account transfer will be double counted when owner
makes the deposit for them. Which means owner can withdraw more than what he actually has and this
withdrawal will come with a cost to other users, as the cost will be taken from their share.
Secondly: "Diminished Yield When Owner Deposits". When an owner deposits their shares are reduced in
anticipation of them being increased later on in the respective internal deposit function. However, before
they are increased the account will get yield based on shares. Since it was reduced early the yield will also be
reduced. Leading to a loss of yield for the owner whenever they deposit. And finally, another issue is: "Initial
Stakes Of Owner Won't be Counted in Reward Calculation".
During initialization, Owners GMX's and GLP's will be staked automatically but these won't be counted in
accumulatedGmxWethPerShare and accumulatedGlpWethPerShare until owner does a ownerDeposit. Hence
the yield accrued in between will be given to other depositors. Moreover it won't be possible for owner to
deposit more than their share amounts in one step because amount will be withdrawn from share.
Furthermore, it is not even possible to deposit new GLP tokens to the vault by the owner because there is no
transfer capability in ownerDeposit function for GLP.

## Recommendation
While it is possible to try to implement a fix for every issue individually, the optimal resolution that will fix all
the issues would be to:
• Remove the ownerDeposit function altogether and vest the initial amounts for the owner during
initialization.
• Add an owner check to deposit function to update ownerInitialGMX and ownerInitialGLP variables.
These changes will basically remove the difference between owner's deposit for the already staked tokens
and owner's new deposits with transferring new tokens and will prevent all issues mentioned above from
occurring.
