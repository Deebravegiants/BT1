# [M] Any signature is valid if the signer is address(0)

## Summary
Severity: Medium
Contest weight: 0.0436
Dataset id: 7462
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an authentication bypass caused by improper handling of the return value from the EVM cryptographic primitive ecrecover. In the contract’s SignatureLib, the function recoverSigner calls ecrecover directly and then compares the recovered address with a stored signer address. When ecrecover is given an invalid signature it returns the zero address (address(0)). Because the contract does not explicitly reject a zero address and because the signer variable may remain uninitialised (defaulting to address(0) if the constructor does not set it), the comparison "recovered == signer" evaluates to true for any invalid signature. Consequently, any caller can present an arbitrary or empty signature and the contract will treat it as valid, allowing the caller to execute privileged actions such as buying shares without possessing a legitimate authorization. This flaw manifests only when the signer field is zero, which can happen if the deployment script forgets to pass a proper signer or if the constructor logic is omitted. The impact is that unauthorized participants can acquire shares, potentially diluting legitimate investors and compromising the economic model of the protocol. From a user’s perspective the symptom is that shares appear to be allocated to unknown addresses, or that a user can trigger a purchase transaction without providing a real signature, contradicting the expectation that a cryptographic proof is required. The issue was discovered during a manual audit by ThreeSigma, who noticed that the library relied on ecrecover’s raw output and did not guard against the zero‑address edge case. The bug is subtle because ecrecover returning address(0) is a documented behaviour, yet many developers assume that a recovered address will always be non‑zero for a signed message, leading to a false sense of security. To remediate the problem the contract should either enforce that the signer variable is never zero at deployment, or, more robustly, replace the raw ecrecover call with OpenZeppelin’s ECDSA wrapper which explicitly checks for a zero address and reverts on invalid signatures. This change restores the intended authentication guarantee and prevents the accidental acceptance of any signature, thereby aligning the contract’s behaviour with its business logic that only authorised signers may trigger share purchases.

## Recommendation
Use Openzeppelin's wrapper ECDSA, which checks for address(0) explicitly.
