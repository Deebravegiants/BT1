# [?] Fix Rayon deadlock in test utils (#4837)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2023-10-18
Source: https://github.com/sigp/lighthouse/commit/192d44271849e744fc7ec0c574c6564eea49f015
Type: security-commit

## Details
Fix Rayon deadlock in test utils (#4837)

## Issue Addressed

Fix a deadlock in the tests that was causing tests on tree-states to run for hours without finishing: https://github.com/sigp/lighthouse/actions/runs/6491194654/job/17628138360.

## Proposed Changes

Avoid using a Mutex under the Rayon `par_iter`. Instead, use an `AtomicUsize`. I've run the new version several times in a loop and it hasn't deadlocked (it was deadlocking consistently on tree-states).

## Additional Info

The same bug exists in unstable and tree-states, but I'm not sure why it was triggering so consistently on the tree-states branch.
