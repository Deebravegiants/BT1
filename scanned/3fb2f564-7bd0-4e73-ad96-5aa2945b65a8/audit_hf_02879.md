# [M] address(0) can be added as a pair, triggering taxes on burn

## Summary
Severity: Medium
Contest weight: 0.0193
Dataset id: 16158
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of the ability to register the zero address (address(0)) as a liquidity pair in the contract's internal pairs mapping. The root cause is that the function that records a new AMM pair does not validate that the supplied address is non‑zero before inserting it into the mapping. Because the contract later treats any entry in the pairs mapping as a taxable pair, a burn operation that sends tokens to address(0) is mistakenly identified as a transfer to a taxable pair, causing the burn to be subject to the contract's tax logic. An attacker or a careless user can trigger this by calling the pair‑registration function with address(0) or by exploiting a public interface that allows arbitrary pair addition. Once the zero address is present, any subsequent token burn will incur the same tax that would normally be applied to a regular trade, reducing the amount of tokens that are actually destroyed and effectively diverting a portion of the burned amount to the tax collector. This leads to unexpected loss of funds for token holders who expect a full burn, and it breaks the accounting assumption that burning tokens does not generate tax revenue. The issue manifests whenever a burn is performed after the zero address has been added to the pairs mapping; it does not require any special permissions beyond the ability to add a pair. Users see a discrepancy between the amount they intended to burn and the amount that is deducted from their balance, often observing that their balance decreases by less than the burn amount while the tax address receives an unexpected transfer. The problem was discovered during a manual audit of the pair‑registration logic, where the lack of a non‑zero address check was noted. Because the zero address is a valid Solidity value and the contract does not emit a specific warning, the bug can remain hidden until a burn is executed and the tax is observed. The appropriate fix is to add an explicit require statement that reverts if the supplied pair address is address(0) before writing to the pairs mapping, or to use a modifier that validates all external addresses used in pair registration. This falls under the broader class of input‑validation errors where unchecked zero addresses lead to unintended state changes and financial mis‑calculations.

## Recommendation
Revert if the pair does not exist in recordAmmPairWith().
