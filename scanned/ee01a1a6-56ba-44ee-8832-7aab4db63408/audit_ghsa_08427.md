# [M] Free5GC AMF Bypasses UE Security Capabilities on NGAP PathSwitchRequest

## Summary
Severity: Medium
Advisory: GHSA-77x9-rf64-92gv
CVE: CVE-2026-42081
CWE: CWE-358
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-77x9-rf64-92gv
Type: github-advisory

## Affected
- Go: `github.com/free5gc/amf` — affected >=0

## Details
### Summary
The AMF in Free5GC v4.2.1 does not verify the UE Security Capabilities received in NGAP PathSwitchRequest messages against its locally stored values, as mandated by 3GPP TS 33.501 §6.7.3.1. A malicious gNB can overwrite the AMF's stored UE security capabilities with arbitrary values, which are then propagated in PathSwitchRequest Acknowledge messages and subsequent Handover Request messages. This leads to persistent handover denial-of-service for affected UEs.

### Details
**Affected File:** `amf/internal/ngap/handler.go` — `handlePathSwitchRequestMain` function

**Root Cause:**

When the AMF receives a PathSwitchRequest during an Xn-handover, it processes the UESecurityCapabilities IE by directly overwriting the stored values without comparing them to the previously stored capabilities:

```go
if uESecurityCapabilities != nil {
    amfUe.UESecurityCapability.SetEA1_128_5G(uESecurityCapabilities.NRencryptionAlgorithms.Value.Bytes[0] & 0x80)
    amfUe.UESecurityCapability.SetEA2_128_5G(uESecurityCapabilities.NRencryptionAlgorithms.Value.Bytes[0] & 0x40)
    amfUe.UESecurityCapability.SetEA3_128_5G(uESecurityCapabilities.NRencryptionAlgorithms.Value.Bytes[0] & 0x20)
    amfUe.UESecurityCapability.SetIA1_128_5G(uESecurityCapabilities.NRintegrityProtectionAlgorithms.Value.Bytes[0] & 0x80)
    amfUe.UESecurityCapability.SetIA2_128_5G(uESecurityCapabilities.NRintegrityProtectionAlgorithms.Value.Bytes[0] & 0x40)
    amfUe.UESecurityCapability.SetIA3_128_5G(uESecurityCapabilities.NRintegrityProtectionAlgorithms.Value.Bytes[0] & 0x20)
}
```

**3GPP TS 33.501 §6.7.3.1 requires three actions, none of which are implemented:**

1. **Verification (SHALL):** "The AMF shall verify that the UE's 5G security capabilities received from the target gNB/ng-eNB are the same as the UE's 5G security capabilities that the AMF has locally stored."
   → Not implemented. The AMF unconditionally overwrites stored values.

2. **Correction (SHALL):** "If there is a mismatch, the AMF shall send its locally stored 5G security capabilities of the UE to the target gNB/ng-eNB in the Path-Switch Acknowledge message."
   → Not implemented. The PathSwitchRequestAcknowledge contains the corrupted values.

3. **Logging (SHALL):** "The AMF shall support logging capabilities for this event and may take additional measures, such as raising an alarm."
   → Not implemented. No mismatch detection or logging exists.

**Propagation:**

The corrupted values are propagated in:
- **PathSwitchRequestAcknowledge:** Contains corrupted UESecurityCapabilities (demonstrated in pcap)
- **Subsequent HandoverRequest messages:** AMF sends corrupted capabilities to target gNBs

Per TS 38.413 §8.4.2.4, if the supported algorithms in the UE Security Capabilities do not match any allowed algorithms configured in the target gNB, the target gNB is required to reject the procedure using a HANDOVER FAILURE message.

### PoC
**Environment:**
- Free5GC v4.2.1 AMF (Docker container) with full NF stack (NRF, AUSF, UDM, UDR, NSSF, PCF, SMF, UPF)
- UERANSIM v3.2.7 gNB with custom inspection-tool extension
- tshark for packet capture

**Reproduction Steps:**

1. Start Free5GC full stack and register a UE through a gNB (NG Setup → Registration → PDU Session Setup).

2. Send a normal HandoverRequired from the gNB. Capture the resulting HandoverRequest from the AMF and confirm `nRintegrityProtectionAlgorithms = 0xe000` (NIA1, NIA2, NIA3 all supported). This is the baseline.

3. Send a PathSwitchRequest with `nRintegrityProtectionAlgorithms = 0x0000` (all integrity algorithms set to not supported). The AMF responds with PathSwitchRequestAcknowledge.

4. Observe that the PathSwitchRequestAcknowledge contains `nRintegrityProtectionAlgorithms = 0x0000` — the corrupted values are propagated back.

**Observed Result (from pcap capture):**

| Packet | Message | nRintegrityProtectionAlgorithms |
|--------|---------|-------------------------------|
| #20 | HandoverRequest (AMF→gNB) | `0xe000` (NIA1 ✓ NIA2 ✓ NIA3 ✓) — **baseline** |
| #30 | PathSwitchRequest (gNB→AMF) | `0x0000` — **poison** |
| #47 | PathSwitchRequestAcknowledge (AMF→gNB) | `0x0000` (NIA1 ✗ NIA2 ✗ NIA3 ✗) — **corrupted** |

### Impact
**Availability (HIGH):** A malicious gNB can send a single PathSwitchRequest message to corrupt the AMF's stored UE security capabilities for any UE. All subsequent inter-gNB handovers for the affected UE are expected to fail (per TS 38.413 §8.4.2.4), resulting in denial-of-service that persists until the UE performs a new registration.

**Integrity (LOW):** The AMF's internal UE security context is corrupted with attacker-controlled values. These corrupted values are propagated to other network elements via PathSwitchRequestAcknowledge and HandoverRequest messages.

**Who is impacted:** Any deployment using Free5GC as the AMF where a gNB could be compromised or where untrusted gNBs exist (e.g., O-RAN multi-vendor deployments).

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-77x9-rf64-92gv
- https://nvd.nist.gov/vuln/detail/CVE-2026-42081
- https://github.com/free5gc/amf/blame/v1.4.3/internal/ngap/handler.go
- https://github.com/free5gc/free5gc
