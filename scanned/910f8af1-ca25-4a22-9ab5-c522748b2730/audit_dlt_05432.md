# [?] Fix race condition in confirm_quorum test (#5096)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2026-06-30
Source: https://github.com/nanocurrency/nano-node/commit/d91fa07c42e47264f5b0fcc815db837858df0bb5
Type: security-commit

## Details
Fix race condition in confirm_quorum test (#5096)

node.confirm_quorum intermittently failed on slow/contended CI runners at
ASSERT_EQ (1, election->votes ().size ()) with a value of 2. Between
processing send1 and the send_action that drained genesis below quorum, the
backlog scheduler could activate send1's election while genesis was still a
heavy principal representative, letting genesis cast a sub-quorum vote that
was cached permanently. The election's confirmation outcome was never at
risk; only the vote-count assertion was racy.

Drain genesis to zero weight through the ledger directly and insert the
voting key only once that is done, so genesis can never vote on the election
while it still holds weight, regardless of scheduler timing.

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
