# [H] Authlib is vulnerable to Denial of Service via Oversized JOSE Segments

## Summary
Severity: High
Advisory: GHSA-pq5p-34cr-23v9
CVE: CVE-2025-61920
CWE: CWE-20, CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-10-10
Source: https://github.com/advisories/GHSA-pq5p-34cr-23v9
Type: github-advisory

## Affected
- PyPI: `authlib` — affected >=0 <1.6.5

## Details
**Summary**
Authlib’s JOSE implementation accepts unbounded JWS/JWT header and signature segments. A remote attacker can craft a token whose base64url‑encoded header or signature spans hundreds of megabytes. During verification, Authlib decodes and parses the full input before it is rejected, driving CPU and memory consumption to hostile levels and enabling denial of service.

**Impact**

- Attack vector: unauthenticated network attacker submits a malicious JWS/JWT.

- Effect: base64 decode + JSON/crypto processing of huge buffers pegs CPU and allocates large amounts of RAM; a single request can exhaust service capacity.

- Observed behaviour: on a test host, the legacy code verified a 500 MB header, consuming ~4 GB RSS and ~9 s CPU before failing.

- Severity: High. CVSS v3.1: AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (7.5).

Affected Versions
Authlib ≤ 1.6.3 (and earlier) when verifying JWS/JWT tokens. Later snapshots with 256 KB header/signature limits are not affected.

**Proof of concept**

Local demo (do not run against third-party systems):
Download [jws_segment_dos_demo.py](https://github.com/user-attachments/files/22450820/jws_segment_dos_demo.py) the PoC in direcotry authlib/
Run following Command
```
python3 jws_segment_dos_demo.py --variant both --sizes "500MB" --fork-per-case

```
Environment: Python 3.13.6, Authlib 1.6.4, Linux x86_64, CPUs=8 
Sample output: Refined
<img width="1295" height="306" alt="image" src="https://github.com/user-attachments/assets/6dd8410f-bc36-4717-8cee-649bac9bf291" />




The compilation script prints separate “[ATTACKER]” (token construction) and “[SERVER]” (Authlib verification) RSS deltas so defenders can distinguish client-side preparation from server-side amplification. Regression tests authlib/tests/dos/test_jose_dos.py further capture the issue; the saved original_util.py/original_jws.py reproductions still accept the malicious payload.

**Remediation**

- Apply the upstream patch that introduces decoded size limits:

- MAX_HEADER_SEGMENT_BYTES = 256 KB

- MAX_SIGNATURE_SEGMENT_BYTES = 256 KB

- Enforce Limits in authlib/jose/util.extract_segment and _extract_signature.

- Deploy the patched release immediately.

- For additional defence in depth, reject JWS/JWT inputs above a few kilobytes at the proxy or WAF layer, and rate-limit verification endpoints.

**Workarounds (temporary)**

- Enforce input size limits before handing tokens to Authlib.

- Use application-level throttling to reduce amplification risk.

**Resources**

- Demo script: jws_segment_dos_demo.py

- Tests: authlib/tests/dos/test_jose_dos.py

- OWASP JWT Cheat Sheet (DoS guidance)

## References
- https://github.com/authlib/authlib/security/advisories/GHSA-pq5p-34cr-23v9
- https://nvd.nist.gov/vuln/detail/CVE-2025-61920
- https://github.com/authlib/authlib/commit/867e3f87b072347a1ae9cf6983cc8bbf88447e5e
- https://github.com/authlib/authlib
- https://lists.debian.org/debian-lts-announce/2025/10/msg00032.html
