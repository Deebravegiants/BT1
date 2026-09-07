# [M] CL-2021-47: Block packing bug

## Summary
Severity: Medium
Chain: Ethereum (consensus layer)
Component: All clients
Published: 2021-12-01
Source: https://github.com/ethereum/consensus-specs/blob/dev/specs/phase0/validator.md#voluntary-exits<br><br>
Type: ef-disclosure

## Details
Affected Clients: All clients
Uid: CL-2021-47
Bug: Block packing bug
Summary: An attacker could poison the mempool by slashing and exiting a validator in the same block, which could halt block production as the slashing is processed first which would cause the exit to fail. This happens due to blocks being packed independently of each other.
Links: [https://github.com/ethereum/consensus-specs/blob/dev/specs/phase0/validator.md#voluntary-exits<br><br>](https://github.com/ethereum/consensus-specs/blob/dev/specs/phase0/validator.md#voluntary-exits)[https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H/E:H/RL:O/RC:C&version=3.1](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H/E:H/RL:O/RC:C&version=3.1)
Fixed Date: 2021-10-27
Published: 2021-12-01
Cvss: 6.5
Severity: Medium
Bounty Hunter: Nishant (Prysm)
Bounty Points: 4600
Bounty Reward (Usd): 0
