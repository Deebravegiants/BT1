# [?] splice: Test fix for test crash splice

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2025-05-14
Source: https://github.com/ElementsProject/lightning/commit/b76c0c1d376b3667e5fd758dee9ddd8f07c9e8a9
Type: security-commit

## Details
splice: Test fix for test crash splice

Fix a typo where the commit sig message ordering was not handled correctly for the first element.

We need to use msg_batch[0] to get the first post-sorted result instead of the original msg.

Changelog-None
