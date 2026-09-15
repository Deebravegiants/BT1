# [H] Horcrux Double Sign Possibility

## Summary
Severity: High
Advisory: GHSA-6wxf-7784-62fp
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:A (CVSS_V4)
Published: 2025-03-07
Source: https://github.com/advisories/GHSA-6wxf-7784-62fp
Type: github-advisory

## Affected
- Go: `github.com/strangelove-ventures/horcrux/v3` — affected >=3.1.0 <3.3.2

## Details
# **Horcrux Incident Disclosure: Possible Double-Sign**

## **Summary**

On March 6, 2025, a Horcrux user (01node) experienced a double-signing incident on the Osmosis network, resulting in a 5% slash penalty (approximately 75,000 OSMO or $20,000 USD). After thorough investigation, we have identified a race condition in Horcrux's signature state handling as the root cause. This vulnerability was introduced in July 2023 as part of PR [\#169](https://github.com/strangelove-ventures/horcrux/pull/169) and affects all Horcrux versions from v3.1.0 through v3.3.1. A fix has been developed and is being deployed immediately.

## **Probability**

The bug has an extremely low probability of occurrence, affecting one validator out of hundreds that have been using the affected software versions to validate over the past few years. In the added tests, the probability on typical hardware is in the range of 1 in 1 billion per signed vote due to the root cause needing two independent events to occur within approximately the same microsecond duration.

## **Severity**

While rare, it is of high severity, as the double-sign (tombstone) slash on most Cosmos chains is typically 5% to the validator’s self stake and the stake of delegators that is delegated to the validator. The bug is not exploitable, so the urgency to apply this patch is purely around avoiding the race condition to remove tombstone risk.

## **Impact**

* One known validator (01node) was affected  
* The validator and its delegators were slashed 5% of their stake delegated with the validator (\~75,000 OSMO, \~$20,000 USD)  
* The incident occurred at Osmosis block height 30968345

## **Technical Details**

### **Root Cause**

The issue was a race condition in the signature state handling code. When two sign requests arrive nearly simultaneously for the same Height-Round-Step (HRS), a split read-write lock pattern allowed both to proceed when they should have been serialized. This vulnerability allowed Horcrux to sign both a "yes" vote (non-nil BlockID) and a "no" vote (nil BlockID) for the same block, which constitutes a double sign violation.

In the affected code:

1. The `HRSKey()` method used a read lock to check the current signature state  
2. The `cacheAndMarshal()` method used a separate write lock to update the state

Because the usage of these operations unlocked in the middle to perform checks rather than occurring under a single lock, they were not atomic. Very rarely, two concurrent signature requests could both pass the initial safety check before either one updated the state, leading to a double signature.

Evidence from logs shows two different signatures were produced within 1.5 milliseconds of each other:

```
DuplicateVoteEvidence{
  VoteA: Vote{69:03C016AB7EC3 30968345/00/SIGNED_MSG_TYPE_PREVOTE(Prevote) 000000000000 BEEB4E1F5432 000000000000 @ 2025-03-06T21:35:48.759070033Z}, 
  VoteB: Vote{69:03C016AB7EC3 30968345/00/SIGNED_MSG_TYPE_PREVOTE(Prevote) 817EB28D720F FAE04CB3CF89 000000000000 @ 2025-03-06T21:35:48.760639069Z}
}
```

This matches the signatures reported in the Horcrux cosigner logs:

* Cosigner-1: `sig=FAE04CB3CF89 ts="2025-03-06 21:35:48.760639069 +0000 UTC"`  
* Cosigner-2: `sig=BEEB4E1F5432 ts="2025-03-06 21:35:48.759070033 +0000 UTC"`

The race condition allowed both signatures to be validated and broadcast, resulting in the double sign.

### **Fix**

The fix implements a single mutex lock that covers both the reading of the current signature state and the subsequent writing of any updates:

```go
func (signState *SignState) Save(
	ssc SignStateConsensus,
	pendingDiskWG *sync.WaitGroup,
) error {
	signState.mu.Lock()
	if err := signState.getErrorIfLessOrEqual(ssc.Height, ssc.Round, ssc.Step); err != nil {
		signState.mu.Unlock()
		return err
	}

	// HRS is greater than existing state, move forward with caching and saving.
	signState.cache[ssc.HRSKey()] = ssc
	
	// Update state
	// ...
	
	signStateCopy := signState.copy()
	signState.mu.Unlock()
	
	// Perform disk operations
	// ...
}
```

By using a single lock for both operations, we ensure that only one signature request for a given HRS can proceed at a time, eliminating the race condition.

## **Timeline**

* **July 6, 2023**: Vulnerability introduced in PR \#169 "sign state signaling"  
* **March 6, 2025, \~21:35 UTC**: 01node double-sign occurred at Osmosis block height 30968345  
* **March 6, 2025, \~23:25 UTC**: 01node reported the incident  
* **March 7, 2025, \~1:03 UTC**: Root cause identified and fix developed  
* **March 7, 2025**: Fix released and deployed (planned)

## **Recommendations**

All Horcrux users running versions v3.1.0 through v3.3.1 should update to the patched version immediately. The fix is backward compatible and does not require any configuration changes.

Update instructions:

1. Download the v3.3.2 release binary or container image, or build from source on the v3.3.2 tag  
2. Apply the release binary or image to your deployment  
3. Restart your cosigner processes one at a time to ensure continuous validator operation

## **Preventive Measures**

To prevent similar issues in the future, we are implementing the following measures:

1. Adding additional tests focused on concurrent signature requests  
2. Implementing a comprehensive review of all critical-path mutex usage in the codebase  
3. Adding additional logging and monitoring for potential double-sign conditions  
4. Enhancing the code review process for security-critical components

## **Conclusion**

We deeply regret this incident and the impact it has had on affected validators. Horcrux was specifically designed to prevent double-signing, and we take this failure extremely seriously. We are committed to making all necessary improvements to ensure this type of incident cannot occur again.

Strangelove is in direct communication with affected parties and will provide any assistance needed, including detailed technical information about the incident and remediation steps.

We will be working with 01node to reimburse those impacted by the tombstone event slash.

For any questions or concerns regarding this incident, please contact [security@strange.love](mailto:security@strange.love).

## References
- https://github.com/strangelove-ventures/horcrux/security/advisories/GHSA-6wxf-7784-62fp
- https://github.com/strangelove-ventures/horcrux/pull/169
- https://github.com/strangelove-ventures/horcrux/commit/fb49be9baed30942b81b42da2b4f7040a2a83c02
- https://github.com/strangelove-ventures/horcrux
- https://github.com/strangelove-ventures/horcrux/releases/tag/v3.3.2
