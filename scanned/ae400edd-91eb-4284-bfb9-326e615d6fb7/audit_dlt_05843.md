# [?] fix!: sealer: handle initialisation error without panic

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2024-07-15
Source: https://github.com/filecoin-project/lotus/commit/85587dd5b412a3570a1d51f3df1ca8e8a340970d
Type: security-commit

## Details
fix!: sealer: handle initialisation error without panic

storage/pipeline.NewPreCommitBatcher and storage/pipeline.New now have an additional
error return to deal with errors arising from fetching the sealing config.
