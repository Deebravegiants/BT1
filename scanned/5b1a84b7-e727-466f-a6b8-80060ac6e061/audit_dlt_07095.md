# [?] Fix data race on the shared err in the REST duties fetch (#17422)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-08-31
Source: https://github.com/OffchainLabs/prysm/commit/644c5151a91ba7ff9f9c7aa4237b2b39178cc90e
Type: security-commit

## Details
Fix data race on the shared err in the REST duties fetch (#17422)

**What type of PR is this?**

Bug fix

**What does this PR do? Why is it needed?**

`dutiesForEpoch` fetches attester and proposer duties concurrently
through an `errgroup`, but both goroutines assigned the same
function-scoped `err`, declared once above them:

```go
var attesterDutiesContainer *structs.GetAttesterDutiesResponse
var err error                                                    // <- shared
wg.Go(func() error {
    attesterDutiesContainer, err = c.dutiesProvider.AttesterDuties(ctx, epoch, indices)
    if err != nil { ... }
    ...
})
...
wg.Go(func() error {
    proposerDutiesContainer, err = c.dutiesProvider.ProposerDuties(ctx, epoch)   // <- same err
    if err != nil { ... }
```

The sync duties goroutine in between uses `:=` and was already safe;
these two use `=`.

Beyond the race itself, the two goroutines can observe each other's
result in the window between the assignment and the `if err != nil` on
the next line:

- a proposer failure seen by the attester goroutine is reported as
`failed to get attester duties for epoch N`, blaming the wrong request;
- in the other direction an attester failure overwritten by the
proposer's `nil` is dropped, and the goroutine then falls through to
`attesterDutiesContainer.Data` with a nil response.

**Which issue(s) does this PR fix?**

None — filing directly as a small bug fix, per the template note.

**Other notes for review**

No new test: the existing
`TestGetDutiesForEpoch_Error/get_attester_duties_failed` already
reproduces it. Before the change:

```
WARNING: DATA RACE
Write at 0x00c0004130a0 by goroutine 74:
  ...dutiesForEpoch.func3()
      validator/client/beacon-api/duties.go:174

Previous write at 0x00c0004130a0 by goroutine 72:
  ...dutiesForEpoch.func1()
      validator/client/beacon-api/duties.go:114

--- FAIL: TestGetDutiesForEpoch_Error/get_attester_duties_failed
    testing.go:1712: race detected during execution of test
```

After it, `go test -race ./validator/client/beacon-api/ -count=1` passes
for the whole package. Happy to add a dedicated regression test if you
would rather have one that names the behaviour explicitly.

Worth flagging separately: this is invisible to CI today. The Makefile
defaults to `TEST_MODE := no-race` and the workflows run plain `make
test mainnet`, so `mode=race` is never exercised. That is why a race
reachable from an existing unit test has survived.

**Acknowledgements**

- [x] I have read
[CONTRIBUTING.md](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md).
- [x] I have included a uniquely named [changelog fragment
file](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md#maintaining-changelogmd).
- [x] I have added a description with sufficient context for reviewers
to understand this PR.
- [x] I have tested that my changes work as expected and I added a
testing plan to the PR description (if applicable).

Co-authored-by: Claude Opus 5 <noreply@anthropic.com>
Co-authored-by: james-prysm <90280386+james-prysm@users.noreply.github.com>

## Patch
### changelog/pucedoteth_fix-duties-shared-err-race.md
```diff
@@ -0,0 +1,3 @@
+### Fixed
+
+- Fix a data race in the REST validator client: the attester and proposer duty fetches for an epoch ran concurrently but assigned the same `err` variable, so one goroutine could observe the other's error. This could report a proposer failure as an attester failure, or drop an attester error and then panic on the nil response.
```

### validator/client/beacon-api/duties.go
```diff
@@ -109,8 +109,8 @@ func (c *beaconApiValidatorClient) dutiesForEpoch(
 	var wg errgroup.Group
 
 	var attesterDutiesContainer *structs.GetAttesterDutiesResponse
-	var err error
 	wg.Go(func() error {
+		var err error
 		attesterDutiesContainer, err = c.dutiesProvider.AttesterDuties(ctx, epoch, indices)
 		if err != nil {
 			return errors.Wrapf(err, "failed to get attester duties for epoch `%d`", epoch)
@@ -171,6 +171,7 @@ func (c *beaconApiValidatorClient) dutiesForEpoch(
 
 	var proposerDutiesContainer *structs.GetProposerDutiesResponse
 	wg.Go(func() error {
+		var err error
 		proposerDutiesContainer, err = c.dutiesProvider.ProposerDuties(ctx, epoch)
 		if err != nil {
 			return errors.Wrapf(err, "failed to get proposer duties for epoch `%d`", epoch)
@@ -217,6 +218,8 @@ func (c *beaconApiValidatorClient) dutiesForEpoch(
 	}
 
 	dutiesContainer.CurrentEpochDuties = duties
+
+	var err error
 	dutiesContainer.CurrDependentRoot, err = hexutil.Decode(proposerDutiesContainer.DependentRoot)
 	if err != nil {
 		return errors.Wrap(err, "failed to decode current dependent root")
```
