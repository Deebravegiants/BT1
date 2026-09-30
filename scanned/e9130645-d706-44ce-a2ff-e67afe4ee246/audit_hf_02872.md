# [M] Stuck tokens due to not using SafeTransfer

## Summary
Severity: Medium
Contest weight: 0.0148
Dataset id: 16151
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from a token reclamation function that transfers ERC20 tokens out of the contract without employing the SafeERC20.safeTransfer wrapper. By calling the raw token.transfer method and ignoring its return value, the contract assumes a successful transfer even when the token contract deviates from the ERC20 specification, returns false, or imposes transfer restrictions such as fees or pausing. This mismatch creates a situation where the reclaimToken routine may appear to complete without reverting, yet the tokens remain locked inside the contract. An attacker can exploit this by depositing a non‑standard or malicious ERC20 token that deliberately causes transfer to fail silently; when the owner later invokes reclaimToken, the call will not revert, the function will not detect the failure, and the assets become unrecoverable. The impact is loss of funds for the contract owner and any users who trusted the protocol to handle those tokens, effectively breaking the accounting guarantees of the system. The issue manifests whenever reclaimToken is used for tokens that do not strictly follow the ERC20 return‑value convention or that implement additional logic in their transfer function. It was discovered during a manual audit where the code path was inspected and the absence of SafeERC20 usage was noted. Because the failure does not emit an error event and the UI may simply show that the contract balance is unchanged, the problem can be hard to spot without deep testing. The proper remediation is to replace the direct transfer call with SafeERC20.safeTransfer, or at minimum to check the boolean return value and revert on false, thereby ensuring that any transfer failure aborts the transaction and prevents tokens from becoming permanently stuck. This class of bug falls under unsafe ERC20 handling, where missing safety checks lead to token loss and broken business logic, such as users expecting a refund or withdrawal but receiving nothing, or seeing their balance unexpectedly drop to zero.

## Recommendation
Recommendation not found
