# [M] Changing committee to a higher signature threshold will render a request from the previous committee un-processable

## Summary
Severity: Medium
Chain: Smart contract
Component: Most--Aleph-Zero-Bridge
Published: 2024-03-30
Source: https://github.com/hats-finance/Most--Aleph-Zero-Bridge-0xab7c1d45ae21e7133574746b2985c58e0ae2e61d/issues/63
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** @rnemes4
**Submission hash (on-chain):** 0x19c4ac85b9934ad8658ebdf55086e7b84773f7e023ba43c39f25fdb00a9fb99c
**Severity:** medium

**Description:**
## Title: 
Changing committee to a higher signature threshold will render a request from the previous committee un-processable

## Severity: 
Medium

## Description
The function `azero/contracts/most/lib.rs::receive_request` incorrectly uses the current committee signature threshold value as can be seen in the following snippet:

```Rust
let signature_threshold = self
                .signature_thresholds
                .get(data.committee_id) // @audit This shuld be using `committee_id` instead of `data.committee_id`?
                .ok_or(MostError::InvalidThreshold)?;
```

This means that a request from a previous committee with a lower threshold than the current would not be able to be processed if the committee members are changed and the threshold is increased.

### Scenario:
- An initial committee is setup with 4 members charlie, dave, eve and ferdie with a threshold of 4
- Alice creates a request 
- A new committee is created with 5 members charlie, dave, eve, mat and jenny with a threshold of 5
- Alices request is sent by charlie, dave, eve and ferdie, how ever the request will not get processed due to not meeting the current threshold of 5
- Alices request will be stuck and the funds she sent with will not be recoverable unless a new committee is created with exactly the same members and threshold as the original committee

## Recommendation
In order top fix this issue the following ammendment is recommended

```Rust
let signature_threshold = self
                .signature_thresholds
                .get(committee_id) // @audit This shuld be using `committee_id` instead of `data.committee_id`?
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Most--Aleph-Zero-Bridge-0xab7c1d45ae21e7133574746b2985c58e0ae2e61d/issues/63_
