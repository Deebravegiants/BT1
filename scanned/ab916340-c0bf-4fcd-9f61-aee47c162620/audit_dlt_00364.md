# [?] [dkg] Fix security and DoS issues in ChunkyDKG manager (#19544)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-04-28
Source: https://github.com/aptos-labs/aptos-core/commit/cc0d3a963c93c58045a5124bd94f68964fbad04b
Type: security-commit

## Details
[dkg] Fix security and DoS issues in ChunkyDKG manager (#19544)

* [dkg] Bind epoch into AggregatedSubtranscript signature to prevent cross-epoch replay

The AggregatedSubtranscript (which validators sign during certification)
did not include the epoch, allowing a valid multi-sig from epoch N to be
replayed in epoch N+1 if the validator set overlaps. Add dealer_epoch to
AggregatedSubtranscript so the BCS hash (and thus the signature) is
epoch-dependent. Also verify dealer_epoch matches metadata.epoch in the
VM execution path.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* [dkg] Replace Vec<Player> with BitVec for dealer sets in AggregatedSubtranscript

Vec<Player> allowed duplicates, reordering, and inflation of the dealer
list, which could produce malformed signatures or enable DoS via inflated
lists triggering expensive aggregation. Replace with BitVec (bitmask over
validator indices), which inherently prevents duplicates, enforces
canonical order, and bounds size to num_validators bits — matching the
existing AggregateSignature pattern. Validation on receipt is now just
bitmask length and popcount checks.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* [dkg] Harden ChunkyDKG signature request handling: state, rate-limit, spawn_blocking

- Accept signature requests in Finished state (not just
  AwaitAggregatedSubtranscriptCertification), so validators continue
  helping peers after completing their own DKG.
- Rate-limit to one concurrent handler per sender (previously only
  deduplicated same-hash retries, allowing different-hash spam).
- Move CPU-heavy subtranscript aggregation into spawn_blocking to
  avoid blocking the async runtime.
- Refactor handle_subtranscript_signature_request into focused helpers:
  resolve_subtranscripts (bitmask validation, local check, polling,
  fetching) and aggregate_and_sign (aggregation + hash verification +
  signing in spawn_blocking).

_Trimmed to 38 lines — full report: https://github.com/aptos-labs/aptos-core/commit/cc0d3a963c93c58045a5124bd94f68964fbad04b_
