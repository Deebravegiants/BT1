# [M] NLTK: SSRF Fail-Open in validate_network_url() via DNS Resolution Failure

## Summary
Severity: Medium
Advisory: GHSA-3gqm-fcw5-w839
CVE: CVE-2026-63311
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-3gqm-fcw5-w839
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.10.0

## Details
There is an SSRF vulnerability in NLTK 3.9.4's network URL validation. The validate_network_url() function in nltk/pathsec.py fails open when DNS resolution returns an error.

The _resolve_hostname() helper at lines 193-234 catches OSError and ValueError during socket.getaddrinfo() and returns an empty list []. When this happens, the validation loop in validate_network_url() iterates over nothing (for addr in resolved: ... never executes), with no else/fallback check. The function returns normally, and urlopen() proceeds to make the request without any IP validation.

This means:
1. If DNS is temporarily unavailable, ALL SSRF protections are disabled
2. DNS rebinding attacks bypass the check after the LRU cache entry expires
3. In environments with unreliable resolvers, the protection is permanently bypassed

PoC:
```python
import nltk.pathsec
import unittest.mock

# Simulate DNS failure
with unittest.mock.patch('socket.getaddrinfo', side_effect=OSError('DNS unavailable')):
    # This SHOULD raise but doesn't -- fails open
    nltk.pathsec.validate_network_url('http://169.254.169.254/latest/meta-data/')
    # Returns normally, allowing SSRF to cloud metadata
```

The correct behavior is fail-closed: if DNS resolution fails, the URL should be REJECTED (not allowed). The function should raise an exception or return a failure status when _resolve_hostname() returns an empty list.

This is distinct from CVE-2024-39705 (which addressed pickle deserialization) and CVE-2026-33236 (which addressed XML path traversal). This finding targets the newly-added pathsec.py security layer introduced to fix those earlier issues.

Suggested fix: Add an explicit check after _resolve_hostname() returns: if the result is empty, raise a SecurityError. Never allow a URL request to proceed when IP validation was impossible.

CVSS Note: The CVSS use SC:H (High subsequent confidentiality) because the advisory explicitly identifies cloud metadata endpoints (169.254.169.254) as an attack target. Access to AWS IMDS or GCP metadata exposes credentials or service account tokens, which constitutes High-impact disclosure on downstream systems. This justifies SC:H over NVD's SC:L.

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-3gqm-fcw5-w839
- https://nvd.nist.gov/vuln/detail/CVE-2026-63311
- https://github.com/nltk/nltk/pull/3582
- https://github.com/nltk/nltk/commit/4a820afa58810cd05049b6c6eae306694d6cfe65
- https://github.com/nltk/nltk
- https://github.com/nltk/nltk/releases/tag/v3.10.0
- https://github.com/pypa/advisory-database/tree/main/vulns/nltk/PYSEC-2026-3723.yaml
- https://www.vulncheck.com/advisories/nltk-before-ssrf-via-dns-resolution-failure
