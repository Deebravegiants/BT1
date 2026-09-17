# [M] 5.2 Unhandled Stake Slashing on Kiln

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Risk Accepted

When computing the managed assets of an external position on Kiln, the system assumes the position
holds validatorCount * 32 ETH + address(this).balance, thus not considering any stake
slashing that may have occurred. This could lead to an over-evaluation of the position if the stake gets
slashed on a validator.

Risk accepted:

Avantgarde Finance replied:

```
Rewards and slashing are not included in the
current position valuation, as this requires external oracle monitoring of
the consensus layer. The actual position value will deviate by some
percent from the ideal value, which will generally tend to be more and
more undervalued if we assume consensus rewards outweigh slashing
in most cases. For now, managers will need to be aware of this, and if
they require more precision, we can integrate a simple oracle to
monitor the delta.
```


Here, we list findings that have been resolved during the course of the engagement. Their categories are
explained in the Findings section.

Below we provide a numerical overview of the identified findings, split up by their severity.

```
Critical-Severity Findings 0
```
```
High-Severity Findings 0
```
```
Medium-Severity Findings 1
```
- lendAndStake() May Interact With Two Pools and Leave Tokens Behind Code Corrected

```
Low-Severity Findings 3
```
- Event Emitted When Non-Existing Pool Is Removed Code Corrected
- Missing Sanitization for _feeBps Code Corrected
- Validation for Balancer Staking Code Corrected
