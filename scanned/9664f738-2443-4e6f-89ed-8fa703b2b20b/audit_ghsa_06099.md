# [M] Lemur: SSRF protection in certificate revocation checking bypassable via HTTP redirects and DNS rebinding (incomplete fix for GHSA-54vg-pfh7-jq95)

## Summary
Severity: Medium
Advisory: GHSA-f3qq-49m6-rw8f
CVE: CVE-2026-70667
CWE: CWE-367, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-f3qq-49m6-rw8f
Type: github-advisory

## Affected
- PyPI: `lemur` — affected >=0 <1.9.3

## Details
## Summary
The SSRF mitigation added for GHSA-54vg-pfh7-jq95 (`_validate_revocation_url()` in `lemur
/certificates/verify.py`) can be bypassed. An operator-role user who uploads a certificate with attacker-controlled CRL/OCSP extensions can still make Lemur reach internal destinations (RFC1918, loopback, link-local 169.254.169.254) during verification.

## Affected version
Tested against `main` (the commit that introduced `_validate_revocation_url`). The 1.9.2 release predates that guard and is vulnerable to the original SSRF (GHSA-54vg-pfh7-jq95) directly; this bypass applies to the unreleased mitigation in `main`. Please map the affected range to whichever release will first contain `_validate_revocation_url`.

## Bypass 1 — HTTP redirect (deterministic)
The guard validates only the URL in the certificate; the CRL fetch then follows redirects without re-validating the target:
```python
# lemur/certificates/verify.py:174
response = requests.get(point, timeout=(3.05, 6))   
```
The attacker hosts the CRL URL on a public host they control (passes the guard); that host returns `302 Location: http://169.254.169.254/...`. `requests` follows it to the internal target the guard never inspected.

## Bypass 2 — DNS rebinding / TOCTOU (probabilistic)
The guard resolves once during validation; the fetch re-resolves independently:
```python
# lemur/certificates/verify.py:51
addr = ipaddress.ip_address(socket.gethostbyname(hostname))
```

A low-TTL attacker name that answers a public IP at check time and an internal IP at fetch time passes the guard but is fetched internally. Same gap affects the OCSP path (`openssl ocsp -url <url>`, verify.py:90-99).

## Relationship to GHSA-54vg-pfh7-jq95
Incomplete-fix of that mitigation, not a duplicate. Bypass 1 is not mentioned there; bypass 2 is the rebinding gap that advisory's remediation text anticipated ("pins the resolved IP") but the code does not implement.

## Affected endpoint
`POST /api/1/certificates/upload` (operator role) → verify_string → crl_verify / ocsp_verify. Triggered when verification runs (e.g. the check_revocation task).

## PoC
1. Generate a cert with `crlDistributionPoints = URI:http://attacker.example/crl`.
2. That host returns `302 Location: http://169.254.169.254/latest/meta-data/...` (bypass 1), or use a low-TTL rebinding name (bypass 2).
3. Upload via `POST /api/1/certificates/upload` as an operator user.
4. Trigger `lemur certificate check_revocation`.
5. Observe the request reach the internal address (`tcpdump -nni any host 169.254.169.254`).

<img width="1140" height="277" alt="poc-1" src="https://github.com/user-attachments/assets/f27b9584-b33a-4b9c-b812-8c60302e1892" />

## Impact
Blind SSRF from the Lemur host: reach internal services and instance metadata (169.254.169.254 without IMDSv2). Response is parsed as a CRL and discarded — reachability/side-effects, not response exfiltration.

## Remediation
- `allow_redirects=False` on CRL fetches (or re-validate every redirect hop).
- Resolve once, pin the IP, connect to the pinned address; route the OCSP URL through the same check.
- Reject names with any internal A/AAAA record.

## References
- https://github.com/Netflix/lemur/security/advisories/GHSA-f3qq-49m6-rw8f
- https://github.com/Netflix/lemur/commit/ed504a830f38a83825b1570302e9f38d6553938a
- https://github.com/Netflix/lemur
- https://github.com/Netflix/lemur/releases/tag/v1.9.3
