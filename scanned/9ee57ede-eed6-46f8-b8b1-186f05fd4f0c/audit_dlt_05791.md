# [?] fix(mempool): converting to uint64 before additions to avoid overflows (#2498)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-03-06
Source: https://github.com/cometbft/cometbft/commit/551fc9b7c4bfd78369d0cc55d95ed4dfe634b50b
Type: security-commit

## Details
fix(mempool): converting to uint64 before additions to avoid overflows (#2498)

Closes #2445
<!--

Please add a reference to the issue that this PR addresses and indicate
which
files are most critical to review. If it fully addresses a particular
issue,
please include "Closes #XXX" (where "XXX" is the issue number).

If this PR is non-trivial/large/complex, please ensure that you have
either
created an issue that the team's had a chance to respond to, or had some
discussion with the team prior to submitting substantial pull requests.
The team
can be reached via GitHub Discussions or the Cosmos Network Discord
server in
the #cometbft channel. GitHub Discussions is preferred over Discord as
it
allows us to keep track of conversations topically.
https://github.com/cometbft/cometbft/discussions

If the work in this PR is not aligned with the team's current
priorities, please
be advised that it may take some time before it is merged - especially
if it has
not yet been discussed with the team.

See the project board for the team's current priorities:
https://github.com/orgs/cometbft/projects/1

-->

---

#### PR checklist

- [ ] Tests written/updated
- [ ] Changelog entry added in `.changelog` (we use
[unclog](https://github.com/informalsystems/unclog) to manage our
changelog)
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments
- [ ] Title follows the [Conventional
Commits](https://www.conventionalcommits.org/en/v1.0.0/) spec

### mempool/clist_mempool.go
```diff
@@ -390,7 +390,7 @@ func (mem *CListMempool) isFull(txSize int) error {
 		txsBytes = mem.SizeBytes()
 	)
 
-	if memSize >= mem.config.Size || int64(txSize)+txsBytes > mem.config.MaxTxsBytes {
+	if memSize >= mem.config.Size || uint64(txSize)+uint64(txsBytes) > uint64(mem.config.MaxTxsBytes) {
 		return ErrMempoolIsFull{
 			NumTxs:      memSize,
 			MaxTxs:      mem.config.Size,
```
