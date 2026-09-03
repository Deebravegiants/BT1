# [?] [TrafficControl] Enable DOS protection by default (dryRun)  (#22143)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-05-21
Source: https://github.com/MystenLabs/sui/commit/9006185009afa2fe239fec771a7d067437814a42
Type: security-commit

## Details
[TrafficControl] Enable DOS protection by default (dryRun)  (#22143)

## Description 

In order for the traffic controller to be enabled in any form,
validators must add a `policy-config:` block to their nodes, copying the
examples from:
https://gist.github.com/williampsmith/4de166d8be9bb9e183594d631452fb19

I can't see good reason not to turn traffic controller on in dry-run
mode by default, since it's essentially what we're asking operators to
do in the above guide. The configs I used in
`default_dos_protection_policy()` are just cut and paste from that gist
(I'm not certain those are the best defaults, but seems that Will
thought so)

## Test plan 

I've tested these changes locally.

we currently have 37 mainnet validators with some type of `PolicyConfig`
enabled
<img width="598" alt="image"
src="https://github.com/user-attachments/assets/6a2b9d78-1bf0-40d5-8666-5f762bd39ee4"
/>

and 56 testnet validators:
<img width="450" alt="image"
src="https://github.com/user-attachments/assets/141981c5-c361-4c32-bd3a-3717ee90f147"
/>


---

## Release notes

Check each box that your changes affect. If none of the boxes relate to
your changes, release notes aren't required.

_Trimmed to 38 lines — full report: https://github.com/MystenLabs/sui/commit/9006185009afa2fe239fec771a7d067437814a42_
