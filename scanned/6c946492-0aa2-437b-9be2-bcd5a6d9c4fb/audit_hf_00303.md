# [M] Lack of input checks

## Summary
Severity: Medium
Contest weight: 0.1607
Dataset id: 1515
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an insufficient validation of the economic penalty parameter used during token launch configuration. The protocol relies on a non‑zero penalty to discourage strategic withdrawals that could manipulate the token price during a sale. Because the contract does not enforce that the penalty value be greater than zero at initialization or when created through the factory, an attacker – or an unwary deployer – can set the penalty to zero. When the penalty is zero, the economic deterrent disappears, allowing an adversary to execute a price‑manipulation attack as outlined in the protocol’s whitepaper (page 7). The exploit works by withdrawing large amounts of the token or performing coordinated trades without incurring any cost, thereby distorting the market price and potentially draining funds or invalidating the entire token launch. The impact can be severe for the token launch participants: users may see their expected refunds or token allocations disappear, balances may be reduced to zero, and the launch may be rendered economically meaningless. The issue manifests only when the launch parameters are configured with a zero penalty, which can happen by mistake during deployment or be deliberately set by a malicious launch creator. Because the parameter is a numeric field without explicit bounds, the flaw can be easily overlooked during code review or testing, especially if the default value happens to be zero. The problem was identified during a Code4rena audit, where the auditors noted that the lack of a >0 check contradicts the protocol’s security model. To remediate, the contract should enforce a constraint that the penalty value must be strictly greater than zero either in the initializer function or within the factory that creates launch contracts, ensuring that the economic safeguard is always active. This type of bug belongs to the class of missing input validation or unchecked parameter constraints, which can undermine business logic that assumes a minimum economic cost for certain actions.

## Proof of Concept
The protocol uses economic penalties to punish withdraws to protect against economic price manipulation attacks. If these penalties are set to 0 in the creation of a token launch the sale would be vulnerable to this kind of attack. The penalties should never be 0 for any token sale.

The economic attack that could be done with 0 penalties is detailed on page 7 of the whitepaper.

I consider this to be a medium risk since it could completely invalidate a token launch but it’s still unlikely (but possible) the creators will set penalties to 0. This could be done by mistake or by the creators of the launch event to exploit it themselves.

## Recommendation
Require penalties to be greater than 0 either in the initializer function or in the factory.

Disagree with severity, should be 1 (Low).

I agree with the warden on risk here.
