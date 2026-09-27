# [?] Fix race condition for RW operation of REST handler host (#17092)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-07-06
Source: https://github.com/OffchainLabs/prysm/commit/5547f6456fc1a7835795e4668139617c2a9c4d01
Type: security-commit

## Details
Fix race condition for RW operation of REST handler host (#17092)

**What type of PR is this?**

> Bug fix

**What does this PR do? Why is it needed?**

Make RW operation of REST handler atomic. This can happen when switching
host in fallback scenario.

**Which issue(s) does this PR fix?**

N/A

**Other notes for review**

Running race test like:

```bash
go test -race ./api/rest -run TestHandler_ConcurrentHostSwitch -count=100
```

**Acknowledgements**

- [x] I have read
[CONTRIBUTING.md](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md).
- [x] I have included a uniquely named [changelog fragment
file](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md#maintaining-changelogmd).
- [x] I have added a description with sufficient context for reviewers
to understand this PR.
- [x] I have tested that my changes work as expected and I added a
testing plan to the PR description (if applicable).
