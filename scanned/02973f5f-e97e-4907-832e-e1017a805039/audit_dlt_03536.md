# [H] Rewards accumaulated can stay constant and oftern not increment

## Summary
Severity: High
Chain: Smart contract
Component: 2021-08-yield
Published: 2021-08-16
Source: https://github.com/code-423n4/2021-08-yield-findings/issues/65
Type: code-finding

## Details
# Handle

moose-code


# Vulnerability details

## Impact
rewardsPerToken_.accumulated can stay constant while rewardsPerToken_.lastUpdated is continually updated, leading to no actual rewards being distributed. I.e. No rewards accumulate. 

## Proof of Concept
Line 115, rewardsPerToken_.accumulated could stay constant if there are very quick update intervals, a relatively low rewardsPerToken_.rate and a decent supply of the ERC20 token. 

I.e. imagine the token supply is 1 billion tokens (quite a common amount, note even if a supply of only say 1 million tokens this is still relevant). i.e. 1e27 wei.

Line 115 has 
1e18 * timeSinceLastUpdated * rewardsPerToken_.rate / _totalSupply

timeSinceLastUpdated can be crafted to be arbitrarily small by simply transferring or burning tokens, so lets exclude this term (it could be 10 seconds etc). Imagine total supply is 1e27 as mentioned. 

therefore, 1e18 * rewardsPerToken_.rate / 1e27, which shows that if the rewardsPerToken_.rate is < 1e9, something which is very likely, then the accumulated amount won't increment, as there are no decimals in solidity and this line of code will evaluate to adding zero. While this is rounded down to zero, critically,          rewardsPerToken_.lastUpdated = end; is updated. 


The reason I have labelled this as a high risk is the express purpose of this contract is to reward users with tokens, yet a user could potentially quite easily exploit this line to ensure no one ever gets rewards and the accumulated amount never increases. 

Given a fairly large token supply, and a relatively low emissions rate is set, that satisfies the above equation, for the entire duration of the rewards period, the user simply sends tokens back and forth every couple seconds (gas limitations, but layer 2), to keep the delta timeSinceLastUpdated close to 1. 

This way the accumulated amount will never tick up, but time keeps being counted.

Furthermore, I would say this is high risk as this wouldn't even need an attacker. Given the transfer function is likely often being called by users, timeSinceLastUpdated will naturally be very low anyways. 

Even if not so extreme as the above case, Alberto points out that "rounding can eat into the rewards" which is likely to be prevalent in the current scenario and make a big impact over time on the targeted vs actual distribution.  

Again this problem is more likely to occur in naturally liquid tokens where lots of transfer, mint or burn events occur. 





_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-08-yield-findings/issues/65_
