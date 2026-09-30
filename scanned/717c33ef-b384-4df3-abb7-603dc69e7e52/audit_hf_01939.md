# [M] M-1 Insufﬁcient validation of Pool creation parameters

## Summary
Severity: Medium
Contest weight: 0.1038
Dataset id: 10705
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Every Napier Pool is associated with the Curve TriCrypto pool and consists of three principal tokens. There are speciﬁc requirements for these tokens to ensure the system functions correctly:  
• Those three Principal Tokens MUST have common maturity and underlying with less than or equal to 18 decimals.  
• Those three Principal Tokens MUST be deployed by the same TrancheFactory.  
• The Underlying MUST be the same as the Underlying of the Principal Token within the Base pool.  
• The Base pool MUST be a Curve TriCrypto v2 pool.  
Violation of these constraints may cause unexpected behavior.

## Recommendation
While these parameters are provided by the system owner and are likely to be validated carefully off-chain, we recommend enhancing the validation of these parameters in the smart contract code to also include on-chain veriﬁcation.
