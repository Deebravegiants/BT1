# [?] fix: Fix race condition in privval shutdown (#5934)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2026-07-06
Source: https://github.com/cometbft/cometbft/commit/eabe04b9bfc4867fe491f9fced21fb04553c3fd5
Type: security-commit

## Details
fix: Fix race condition in privval shutdown (#5934)

---

Updates the privval RetrySignerClient to check on shutdown before
retrying.
Without this change it is possible to get into the following shutdown
state:
* Node is requesting a signature from a remote signer
* Shutdown happens on remote signer
* Shutdown happens on node


In this case we have to wait `retries × (timeoutAccept + timeout) ≈
155s` before the node will shut down.

With these changes we will wait a maximum of a single retry timeout
before seeing that `Close` has been called (~3s) and shutdown will
happen after that.

---------

Co-authored-by: mergify[bot] <37929162+mergify[bot]@users.noreply.github.com>
