# [?] fix: update race condition for browser to set the state (#45571)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-08-17
Source: https://github.com/MetaMask/metamask-extension/commit/ef798ef7d8e572e76a5a122eea530e3b902e8773
Type: security-commit

## Details
fix: update race condition for browser to set the state (#45571)

This PR fixed an issue where MetaMask could reopen as a popup after
switching to Sidepanel

## **Description**

<!--
Write a short description of the changes included in this pull request,
also include relevant motivation and context. Have in mind the following
questions:
1. What is the reason for the change?
2. What is the improvement/solution?
-->

## **Changelog**

<!--
If this PR is not End-User-Facing and should not show up in the
CHANGELOG, you can choose to either:
1. Write `CHANGELOG entry: null`
2. Label with `no-changelog`

If this PR is End-User-Facing, please write a short User-Facing
description in the past tense like:
`CHANGELOG entry: Added a new tab for users to see their NFTs`
`CHANGELOG entry: Fixed a bug that was causing some NFTs to flicker`

(This helps the Release Engineer do their job more quickly and
accurately)
-->

CHANGELOG entry: null

## **Related issues**

Fixes:


_Trimmed to 38 lines — full report: https://github.com/MetaMask/metamask-extension/commit/ef798ef7d8e572e76a5a122eea530e3b902e8773_
