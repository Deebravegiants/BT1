# [?] Merge #18376: net: fix use-after-free in tests

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-03-18
Source: https://github.com/litecoin-project/litecoin/commit/a421e0a22f1230abd69b4661a019bed39b72205f
Type: security-commit

## Details
Merge #18376: net: fix use-after-free in tests

7d8e1dec3b26074df1533f715871f79c956cc224 net: fix use-after-free in tests (Vasil Dimov)

Pull request description:

  In PeerLogicValidation::PeerLogicValidation() we would schedule a lambda
  function to execute later, capturing the local variable
  `consensusParams` by reference.

  Presumably this was considered safe because `consensusParams` is a
  reference itself to a global variable which is not supposed to change,
  but it can in tests.

  Fixes https://github.com/bitcoin/bitcoin/issues/18372

  <!--
  *** Please remove the following help text before submitting: ***

  Pull requests without a rationale and clear improvement may be closed
  immediately.
  -->

  <!--
  Please provide clear motivation for your patch and explain how it improves
  Bitcoin Core user experience or Bitcoin Core developer experience
  significantly:

  * Any test improvements or new tests that improve coverage are always welcome.
  * All other changes should have accompanying unit tests (see `src/test/`) or
    functional tests (see `test/`). Contributors should note which tests cover
    modified code. If no tests exist for a region of modified code, new tests
    should accompany the change.
  * Bug fixes are most welcome when they come with steps to reproduce or an
    explanation of the potential issue as well as reasoning for the way the bug
    was fixed.
  * Features are welcome, but might be rejected due to design or scope issues.
    If a feature is based on a lot of dependencies, contributors should first
    consider building the system outside of Bitcoin Core, if possible.
  * Refactoring changes are only accepted if they are required for a feature or
    bug fix or otherwise improve developer experience significantly. For example,
    most "code style" refactoring changes require a thorough explanation why they
    are useful, what downsides they have and why they *significantly* improve
    developer experience or avoid serious programming bugs. Note that code style
    is often a subjective matter. Unless they are explicitly mentioned to be
    preferred in the [developer notes](/doc/developer-notes.md), stylistic code
    changes are usually rejected.
  -->

  <!--
  Bitcoin Core has a thorough review process and even the most trivial change
  needs to pass a lot of eyes and requires non-zero or even substantial time
  effort to review. There is a huge lack of active reviewers on the project, so
  patches often sit for a long time.
  -->

ACKs for top commit:
  sipa:
    ACK 7d8e1dec3b26074df1533f715871f79c956cc224
  practicalswift:
    ACK 7d8e1dec3b26074df1533f715871f79c956cc224
  MarcoFalke:
    ACK 7d8e1dec3b26074df1533f715871f79c956cc224

Tree-SHA512: fe0f6e5fac1976d38dfb249517eef142dcb8837e178d7d199e5e854e3ab428822c6da9d96fe312293d39b6c6cac0c97896f3b5760013db200cccd729ae1b0710

## Patch
### src/net_processing.cpp
```diff
@@ -1127,7 +1127,7 @@ PeerLogicValidation::PeerLogicValidation(CConnman* connmanIn, BanMan* banman, CS
     // combine them in one function and schedule at the quicker (peer-eviction)
     // timer.
     static_assert(EXTRA_PEER_CHECK_INTERVAL < STALE_CHECK_INTERVAL, "peer eviction timer should be less than stale tip check timer");
-    scheduler.scheduleEvery([&] { this->CheckForStaleTipAndEvictPeers(consensusParams); }, std::chrono::seconds{EXTRA_PEER_CHECK_INTERVAL});
+    scheduler.scheduleEvery([this, consensusParams] { this->CheckForStaleTipAndEvictPeers(consensusParams); }, std::chrono::seconds{EXTRA_PEER_CHECK_INTERVAL});
 }
 
 /**
```
