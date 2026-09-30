# [?] fix: avoid panic when event stream request creation fails (#16234)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-07-01
Source: https://github.com/OffchainLabs/prysm/commit/ae9bae08699e2f29f79bb99931a004a3ae960022
Type: security-commit

## Details
fix: avoid panic when event stream request creation fails (#16234)

**What type of PR is this?**


> Bug fix


**What does this PR do? Why is it needed?**

When http.NewRequestWithContext fails in EventStream.Subscribe, we were
still accessing req headers, leading to a potential nil dereference
panic. Now we emit an EventConnectionError and return immediately,
matching the rest of our HTTP error handling patterns and keeping the
event stream failure graceful instead of crashing the goroutine.


**Acknowledgements**

- [x] I have read
[CONTRIBUTING.md](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md).
- [ x I have included a uniquely named [changelog fragment
file](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md#maintaining-changelogmd).
- [x] I have added a description with sufficient context for reviewers
to understand this PR.
- [x] I have tested that my changes work as expected and I added a
testing plan to the PR description (if applicable).

---------

Co-authored-by: james-prysm <90280386+james-prysm@users.noreply.github.com>

## Patch
### api/client/event/event_stream.go
```diff
@@ -73,6 +73,7 @@ func (h *EventStream) Subscribe(eventsChannel chan<- *Event) {
 			EventType: EventConnectionError,
 			Data:      []byte(errors.Wrap(err, "failed to create HTTP request").Error()),
 		}
+		return
 	}
 	req.Header.Set("Accept", api.EventStreamMediaType)
 	req.Header.Set("Connection", api.KeepAlive)
```

### changelog/radik878_fix-return.md
```diff
@@ -0,0 +1,3 @@
+### Fixed
+
+- avoid panic when event stream request creation fails [#16234](https://github.com/OffchainLabs/prysm/pull/16234)
```
