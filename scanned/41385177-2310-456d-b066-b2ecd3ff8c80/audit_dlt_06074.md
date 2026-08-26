# [?] fix: Panic instead of logging error of failing header validation (#2231)

## Summary
Severity: Unknown
Chain: Rollkit
Component: rollkit/rollkit
Published: 2025-05-13
Source: https://github.com/evstack/ev-node/commit/8765196fe32fb96a6c161825e9dbade6af51bf1d
Type: security-commit

## Details
fix: Panic instead of logging error of failing header validation (#2231)

<!--
Please read and fill out this form before submitting your PR.

Please make sure you have reviewed our contributors guide before
submitting your
first PR.

NOTE: PR titles should follow semantic commits:
https://www.conventionalcommits.org/en/v1.0.0/
-->

## Overview
Closes: #2182 

<!-- 
Please provide an explanation of the PR, including the appropriate
context,
background, goal, and rationale. If there is an issue with this
information,
please provide a tl;dr and link the issue. 

Ex: Closes #<issue number>
-->


<!-- This is an auto-generated comment: release notes by coderabbit.ai
-->
## Summary by CodeRabbit

- **Bug Fixes**
- Improved error handling during block publishing to ensure immediate
termination if block header validation fails, enhancing system
reliability.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

---------

_Trimmed to 38 lines — full report: https://github.com/evstack/ev-node/commit/8765196fe32fb96a6c161825e9dbade6af51bf1d_
