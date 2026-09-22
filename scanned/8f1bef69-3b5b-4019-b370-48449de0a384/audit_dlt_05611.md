# [?] fix: prevent negative RequestSize crash when beacon pivot destination advances mid-sync (#11478)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-05-06
Source: https://github.com/NethermindEth/nethermind/commit/61c20c5196800aef79a48b0f82ff276910482d55
Type: security-commit

## Details
fix: prevent negative RequestSize crash when beacon pivot destination advances mid-sync (#11478)

* fix: prevent negative RequestSize crash when beacon pivot destination advances mid-sync

`HeadersSyncFeed.ShouldBuildANewBatch` checked
`_lowestRequestedHeaderNumber == HeadersDestinationNumber`. For beacon
headers, `HeadersDestinationNumber` is `BeaconPivot.PivotDestinationNumber`,
which tracks `Head.Number - Reorganization.MaxDepth + 1` and so advances
upward as the chain head progresses. When it stepped above
`_lowestRequestedHeaderNumber` mid-sync, the `==` check missed it,
`BuildNewBatch` produced a negative `RequestSize`, and
`HeaderStore.FindReversedHeaders` crashed with
`ArgumentOutOfRangeException` on `new Dictionary<>(negativeCount)`.

Widen the guard to `<=` and add a regression test that reproduces the
scenario via mocked `IBeaconPivot`.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

* chore: shorten inline comments per review

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
