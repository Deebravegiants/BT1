# [H] Redeem Sense can be bricked

## Summary
Severity: High
Contest weight: 0.6121
Dataset id: 11421
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a denial‑of‑service and fund‑locking flaw in the Redeemer contract’s redeem workflow. The contract accepts a user‑supplied address (parameter d) and forwards the redemption call to ISense(d).redeem after transferring the lender’s entire token balance into the Redeemer contract. Because the address is not validated, an attacker can provide a malicious contract whose redeem function does nothing. The Redeemer contract therefore moves the principal from the lender to itself, calls the bogus redeem, and completes without reverting. The Sense market never receives the redemption request, so its internal accounting remains unchanged. Subsequent attempts to redeem read the lender’s token balance, which is now zero, causing the Redeemer to call redeem again with an amount of zero. This leaves the original principal permanently locked inside the Redeemer contract, effectively bricking the market. The root cause is an untrusted external call without any whitelist or success check, combined with the assumption that the external contract will always perform the expected operation. Exploitation requires only that the attacker can supply an arbitrary address when invoking redeem, which is allowed by the current interface. The impact is that funds disappear from the borrower’s perspective: users who expect a refund receive nothing, balances remain unchanged, and the protocol loses liquidity for that market. The issue manifests when a user calls redeem with a malicious contract address; it is hard to notice because the transaction does not revert and emits no error, making the failure appear as a successful operation. The vulnerability belongs to the class of untrusted external contract calls (call injection) that lead to denial‑of‑service and asset loss. To remediate, the contract should either restrict the d parameter to a whitelisted Sense contract address or bypass the external call entirely by sending the full principal directly to ISense.redeem, and it should verify that the redemption succeeded (e.g., by checking the returned amount or ensuring the contract’s token balance is reduced).

## Proof of Concept
[This](https://github.com/code-423n4/2022-06-illuminate/blob/main/redeemer/Redeemer.sol#L253:#L262) is how Sense market is being redeemed:
```solidity
IERC20 token = IERC20(IMarketPlace(marketPlace).markets(u, m, p));
uint256 amount = token.balanceOf(lender);
Safe.transferFrom(token, lender, address(this), amount);
ISense(d).redeem(o, m, amount);
```
The problem is that `d` is user supplied input and the function only tries to redeem the amount that was transferred from Lender.

A user can supply malicious `d` contract which does nothing on `redeem(o, m, amount)`. The user will then call Redeemer’s `redeem` with his malicious contract. Redeemer will transfer all the prinicipal from Lender to itself, will call `d` (noop), and finish. Sense market has not been redeemed.

Now if somebody tries to call Sense market’s `redeem` again, the `amount` variable will be 0, and Redeemer will try to redeem 0 from Sense.

All the original principal is locked and lost in the contract, like tears in rain.

## Recommendation
I think you should either use a whitelisted Sense address, or send to `ISense(d).redeem` Redeemer’s whole principal balance.
