# [?] fix: Prevent UI state corruption race condition (#39407)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-01-25
Source: https://github.com/MetaMask/metamask-extension/commit/cd9f09cb53f426385075d04267d78f0682f0f007
Type: security-commit

## Details
fix: Prevent UI state corruption race condition (#39407)

## **Description**

State changes that occur _after_ a UI connection is initialized, but
_before_ the initial state for that connection is retrieved, could get
erroneously sent to the UI as patches (despite the operations being
represented in the initial state already). Certain types of operations
could corrupt the `metamask` state in the UI if they were repeated this
way (e.g. "delete first entry of array" would delete extra entries if
repeated).

This has been prevented by delaying patch tracking until the exact
moment the initial state for the UI connection is retrieved.

This was easiest to accomplish by adding the initial state as a
parameter to the `startUISync` message, which also has the side- effect
of speeding up initial pageload (one less round-trip between the
background and the UI is needed).

This replaces the `getState` call, which is what the UI used to call to
get the initial background state. This call was surrounded by a
16-second timeout, so that the user would not be stuck waiting forever
if it failed. This timeout logic has been migrated to the
`CriticalStartupErrorHandler` class, and is now based on the
`startUISync` method.

[![Open in GitHub
Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MetaMask/metamask-extension/pull/39407?quickstart=1)

## **Changelog**

CHANGELOG entry: Optimize initial page load and prevent rare temporary
UI state corruption

## **Related issues**

N/A

_Trimmed to 38 lines — full report: https://github.com/MetaMask/metamask-extension/commit/cd9f09cb53f426385075d04267d78f0682f0f007_
