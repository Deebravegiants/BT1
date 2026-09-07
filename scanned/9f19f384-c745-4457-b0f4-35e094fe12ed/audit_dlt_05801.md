# [?] fix(tests/befp): fix panic in befp test (#3108)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2024-01-19
Source: https://github.com/celestiaorg/celestia-node/commit/ba3800969143901d01e52e4509fd02d68ca7f887
Type: security-commit

## Details
fix(tests/befp): fix panic in befp test (#3108)

ShareWithProofs collection happens async and it does not guarantee that
Shares at index [1] will be non-nil. Panic happened in `incorrect share
with Proof` when `befp.Shares[1] == nil`

tested with `go test -v -count=300 -run ^TestBEFP_Validate$
github.com/celestiaorg/celestia-node/share/eds/byzantine`
