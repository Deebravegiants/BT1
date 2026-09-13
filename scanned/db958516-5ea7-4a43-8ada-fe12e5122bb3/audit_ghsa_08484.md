# [M] Keylime has a hardcoded attestation challenge nonce that allows replay attacks

## Summary
Severity: Medium
Advisory: GHSA-q8w6-w55c-ccv5
CVE: CVE-2026-6420
CWE: CWE-1241, CWE-294, CWE-329, CWE-547
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-q8w6-w55c-ccv5
Type: github-advisory

## Affected
- PyPI: `keylime` — affected >=7.14.0 <7.14.2

## Details
## CVE-2026-6420: Hardcoded attestation challenge nonce allows replay attacks

### Impact

The `CertificationParameters.generate_challenge()` method in the push attestation protocol uses a hardcoded challenge nonce instead of generating a cryptographically random value. This removes the nonce-based replay protection from TPM quote attestation.

An attacker with root access on a monitored agent node can exploit this by stockpiling valid TPM quotes (using `tpm2_quote` with the known nonce) before compromising the system, then replaying them to evade detection by the verifier. The push attestation timeout (~10s) constrains the generation window, but TPM throughput allows stockpiling ~50-200 quotes, enabling approximately 8-33 minutes of undetected compromise with default settings.

The attack is limited to a single agent node (AK signature binding prevents cross-agent replay). The pull-mode (legacy) attestation path is not affected.

**Affected versions:** >= 7.14.0, <= 7.14.1

**CVSS:** 6.3 Medium (`CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L`)

| Metric | Value | Rationale |
|---|---|---|
| AV | Local | Exploitation requires local access to the agent machine (stop agent, access TPM, run replacement). The network transmission of quotes to the verifier is normal protocol operation. |
| AC | Low | Deterministic attack: publicly visible nonce, standard `tpm2-tools`, no race conditions. |
| PR | High | Root on a legitimate enrolled node is required. The vulnerability does not help gain access -- it only helps evade detection after root is obtained. No value against a machine the attacker already controls. |
| UI | None | Fully automated after initial setup. |
| S | Unchanged | AK signature binding confines impact to the single compromised agent. |
| C | High | Compromised node continues receiving bootstrap keys, payloads, and secrets intended for trusted nodes. |
| I | High | Verifier cannot distinguish a healthy system from a fully compromised one during the evasion window. |
| A | Low | Only the compromised agent's revocation and incident response are suppressed; the system as a whole remains operational. |

The base score does not fully capture the operational severity: Keylime exists to detect machine compromise, so 8-33 minutes of undetected compromise is operationally critical. The fix is a one-line change and should be applied immediately regardless of the base score.

### Patches

The fix restores the original random nonce generation (one-line change in `keylime/models/verifier/evidence.py`):

```python
# Before (vulnerable):
def generate_challenge(self, bit_length):
    # self.challenge = Nonce.generate(bit_length)
    self.challenge = bytes.fromhex("49beed365aac777dae23564f5ad0ec")

# After (fixed):
def generate_challenge(self, bit_length):
    self.challenge = Nonce.generate(bit_length)
```

Users should upgrade to the version containing this fix (7.14.2).

### Workarounds

There is no complete workaround. The following existing mechanisms provide partial mitigation and are already active by default (no configuration needed):

1. **TPM clock monotonicity check** limits each distinct stockpiled quote to a single use, bounding the total evasion time.
2. **Push attestation timeout** (default 10s) prevents the attacker from going silent and constrains the quote generation window.

Reducing `quote_interval` increases the attestation frequency but does not prevent the stockpiling attack.

### References

- CWE-329: Generation of Predictable IV/Nonce (primary -- hardcoded nonce in cryptographic attestation protocol)
- CWE-547: Use of Hard-Coded, Security-relevant Constants (hardcoded constant left in production code)
- CWE-294: Authentication Bypass by Capture-replay (consequence -- enables replay attacks)
- CWE-1241: Use of Predictable Algorithm in Random Number Generator
- Introducing commit: [`2bf91197`](https://github.com/keylime/keylime/commit/2bf91197) via [PR #1814](https://github.com/keylime/keylime/pull/1814)
- TCG TPM 2.0 Library Specification, Part 1, Section 18.4 (TPM2_Quote)
- IETF RATS Architecture (RFC 9334), Section 8 (Freshness)

## References
- https://github.com/keylime/keylime/security/advisories/GHSA-q8w6-w55c-ccv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-6420
- https://access.redhat.com/security/cve/CVE-2026-6420
- https://bugzilla.redhat.com/show_bug.cgi?id=2458889
- https://github.com/keylime/keylime
