# [M] M-02 | Selective Rejection Of Low-Score Certifications

## Summary
Severity: Medium
Contest weight: 0.1883
Dataset id: 8641
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Cyfrin leverages an attestation-resolver pattern to record student scores onchain, with values ranging from s_minimumScore to s_maximumScore. These scores are intended to serve as a transparent and trustable metric for talent evaluation by Cyfrin and third parties. In the current implementation, the system uses safeMint to issue soulbound NFTs. This invokes the onERC721Received hook on the recipient's contract, giving the recipient (student) a chance to inspect the incoming certificate. A student can program this hook to conditionally revert the minting transaction if the score is below a self-imposed threshold. This enables them to:
• Accept only high-score certificates
• Reject lower-score certificates without consequences
As a result, students can selectively curate their onchain reputation, misrepresenting their actual performance. This behavior undermines the credibility and completeness of the certification system. Evaluators relying on these onchain records might be misled, assuming that a student only received high scores, when in fact, lower scores were intentionally blocked from being recorded. Note: With the introduction of EIP-7702, even EOAs can include temporary smart contract logic during a transaction. This means any student, including those using EOAs can now curate their onchain reputation in a misleading way.

## Recommendation
Consider replacing safeMint with a _mint. Since these certificates are intended to be soulbound and non-transferable, there's no need to check for receiver compatibility for handling of NFTs.
