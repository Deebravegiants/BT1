# [H] Taurus multi-party-sig has OT-based ECDSA protocol implementation flaws

## Summary
Severity: High
Advisory: GHSA-7f6p-phw2-8253
Ecosystem: Go
Published: 2024-11-25
Source: https://github.com/advisories/GHSA-7f6p-phw2-8253
Type: github-advisory

## Affected
- Go: `github.com/taurusgroup/multi-party-sig` — affected >=0 <0.7.0-alpha-2025-01-28

## Details
Coinbase researchers reported 2 security issues in our implementation of the oblivious transfer (OT) based protocol [DKLS](https://eprint.iacr.org/2018/499.pdf):

### 1. Secret share recovery attack

If the base OT setup of the protocol is reused for another execution of the OT extension, then a malicious participant can extract a bit of the secret of another participant. By repeating the execution they can eventually recover the whole secret.

Therefore, unlike our comments suggested, you **must not reuse an OT setup** for multiple protocol executions. 

We're adding a warning in the code:

https://github.com/taurushq-io/multi-party-sig/blob/9e4400fccee89be6195d0a12dd0ed052288d5040/internal/ot/extended.go#L114

### 2. Invalid security proof due to incorrect operator

The original 2018 version of the DKLS had a typo in the OT extension protocol when computing the check value in the OT extension: the paper noted a XOR whereas it should be a field multiplication. This erroneous behavior was implemented [in our code](https://github.com/taurushq-io/multi-party-sig/blob/4d84aafb57b437da1b933db9a265fb7ce4e7c138/internal/ot/extended.go#L188). 

The proof of security fails in this case. No concrete attack is known, however.

The [2023 update](https://eprint.iacr.org/2018/499.pdf) of the DKLS paper reported that typo and updated the protocol definition.

~As of 20241124, patching is in progress (branch [otfix](https://github.com/taurushq-io/multi-party-sig/tree/otfix)), but not merged to the main branch yes as the tests fail to pass. We're troubleshooting the issue and will merge into the main branch when it's resolved.~

As of 20250128, a patched version is available in https://github.com/taurushq-io/multi-party-sig/releases/tag/v0.7.0-alpha-2025-01-28, thanks to https://github.com/taurushq-io/multi-party-sig/pull/119.

### Workarounds

Do not reuse an OT setup in the event that an abort is detected, to eliminate the secret recovery attack.
  

### Credits

Thanks to the Coinbase researchers Yi-Hsiu Chen and Samuel Ranellucci for discovering these issues and providing a comprehensive write-up. Thank you to Yehuda Lindell for coordinating the disclosure.
Thanks to Jay Prakash for clarifying the risk of the base setup reuse.
Thanks to @cronokirby for writing the corrected code.

## References
- https://github.com/taurushq-io/multi-party-sig/security/advisories/GHSA-7f6p-phw2-8253
- https://eprint.iacr.org/2018/499.pdf
- https://github.com/taurushq-io/multi-party-sig
- https://github.com/taurushq-io/multi-party-sig/blob/4d84aafb57b437da1b933db9a265fb7ce4e7c138/internal/ot/extended.go#L188
- https://github.com/taurushq-io/multi-party-sig/blob/9e4400fccee89be6195d0a12dd0ed052288d5040/internal/ot/extended.go#L114
- https://github.com/taurushq-io/multi-party-sig/tree/otfix
