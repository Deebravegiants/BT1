# [H] denial of service

## Summary
Severity: High
Contest weight: 0.3431
Dataset id: 1617
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
processWithdrawals can process limited amount in each call.  
An attacker can push to withdrawals enormous amount of withdrawals with amount = 0.  
In order to stop the dos attack and process the withdrawal, the governance needs to spend as much gas as the attacker.  
If the governance doesn’t have enough money to pay for the gas, the withdrawals can’t be processed.

## Proof of Concept
Alice wants to attack vusd, she spends 1 millions dollars for gas to push as many withdrawals of amount = 0 as she can.  
If the governance wants to process the deposits after Alices empty deposits, they also need to spend at least 1 million dollars for gas in order to process Alice’s withdrawals first.  
But the governance doesn’t have 1 million dollars so the funds will be locked.

## Recommendation
Set a minimum amount of withdrawal. e.g. 1 dollar
    
        function withdraw(uint amount) external {
            require(amount >= 10 ** 6);
            burn(amount);
            withdrawals.push(Withdrawal(msg.sender, amount));
        }

Confirming this is an issue. Would classify it as `2 (Med Risk)` because this attack is expensive to carry out.

**[atvanguard (Hubble) resolved](https://github.com/code-423n4/2022-02-hubble-findings/issues/119)**

Would be interested to see the exact gas cost of executing withdraw. The thing is the grievance costs only gas to execute and the withdraw function is relatively cheap from first glance. The main issue here is that it can become SUPER expensive to clear the que in gas. I.e. if the attacker builds up a que of 200 withdrawals, some unknowning sucker is going to pay for more than 200 erc20 transfers in order to get their money out. Thats more than anyone would want to pay, and further since so much gas limit would be needed for this to be executed, to fit into a block you are going to have to pay a huge price. 

So basically it costs attacker x to execute, which means it is also going to cost next user likely even more than x to fix the problem. 

Also the que is not cleared so processWithdrawals becomes a really expensive function. If the items were cleared and set back to zero it would make it less expensive to de-que the que. 

This being said we definitely have this at at least medium severity. $10k in gas to constantly brick users withdrawls from protocol for a week is a serious issue and not the biggest cost for an attack. 

@JasoonS, going to put this as medium. Let’s discuss whether we want to have it as high.

Okay, going to keep this as high severity. The cost to fix the attack can be more than what the attack costs in total. It also burdens a random unsuspecting user with a really high gas cost to try and get their withdrawal. There are many good suggestions on how to fix this.
