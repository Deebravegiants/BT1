# [H] `WETH.allowance`

## Summary
Severity: High
Contest weight: 0.1225
Dataset id: 10202
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the public view function that reports token allowances in the Wrapped Ether (WETH) contract. Instead of returning the value stored in the internal allowance mapping, the function omits the return statement and therefore always yields the default value of zero. This developer oversight causes the contract to misreport the amount that an owner has approved for a spender, regardless of any prior successful calls to the approve method. The root cause is a missing return keyword that prevents the stored _allowance[owner][spender] value from being emitted to the caller. As a result, any external contract or user querying the allowance will observe a zero balance, even though the approval may have been recorded on-chain. This discrepancy can be exploited to cause a denial‑of‑service condition: downstream protocols that rely on a non‑zero allowance to execute transferFrom operations will fail, leading to reverted transactions, stuck funds, or unexpected loss of functionality. Users expecting that their approved spending limits are respected will instead see their allowances reported as zero, experience failed token transfers, and may interpret the behavior as a contract bug or a malicious restriction. The issue manifests whenever the allowance view is called – which is a standard step in ERC‑20 interactions – and therefore affects all token holders, DeFi applications, and any smart contract that depends on WETH's allowance semantics. The problem was uncovered during a formal security audit by Code4rena, where static analysis highlighted the missing return line. Because the bug does not trigger an error or revert, it can remain unnoticed unless tests explicitly compare expected allowance values against the contract’s response. The underlying business logic of ERC‑20 token accounting, which assumes that allowance reflects the approved amount, is violated, breaking trust and potentially causing financial loss. The recommended remediation is to modify the function to return the value stored in the allowance mapping, i.e., `return _allowance[owner][spender];`. Restoring the correct return behavior realigns the contract with ERC‑20 specifications and prevents the zero‑allowance illusion that currently undermines user expectations and protocol integrations.

## Proof of Concept
In this function, the “return” keyword is missing and it will always output 0 in this case.

## Recommendation
L104 should be changed like below.
    
    return _allowance[owner][spender];

The warden has found a minor developer oversight, which will cause the view function `allowance` to always return 0.

Breaking of a core contract such as WETH is a non-starter.

Because I’ve already raised severity of #191 for similar reasons, I think High Severity is appropriate in this case.
