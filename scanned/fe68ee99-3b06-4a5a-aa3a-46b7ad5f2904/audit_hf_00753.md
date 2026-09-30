# [H] H-03 | Old Disputes Can Be Reused After ResetByCouncil

## Summary
Severity: High
Contest weight: 0.3119
Dataset id: 2313
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a market is partially disputed, multiple disputes can be opened in parallel. If one of those
disputes concludes first (e.g., triggering a ResetByCouncil), the market transitions back to
OpenForResolution, and any unclosed disputes remain in storage, still carrying prior votes.
Because those old disputes are never marked as permanently invalid, they can be reused when the
market enters a new resolution flow—allowing a malicious council member to “revive” the
partially-voted dispute and finalize it with minimal new votes.
In the provided example:
1. A market transitions to ResolutionProposed with a “YES” outcome.
2. Two different disputers each open a separate dispute (Dispute #1 and Dispute #2).
3. Dispute #1 closes first (for example, by a majority that sets ResetByCouncil), while Dispute #2
remains open but unresolvable at that moment due to the market status update.
4. The market then resets, returning to OpenForResolution (or even ResolutionProposed again).
5. A malicious council member can propose a new outcome, open a fresh dispute, but then
re-invoke the old, unresolved Dispute #2. Because that older dispute already has partial votes
recorded, the malicious user can cast a single new vote (or minimal votes) to reach a majority,
effectively closing Dispute #2 and imposing its outcome—even though other council members
haven’t re-voted under the new context.

## Recommendation
Invalidate or close all existing disputes when the market transitions from SetByCouncil or
ResetByCouncil back to OpenForResolution.
