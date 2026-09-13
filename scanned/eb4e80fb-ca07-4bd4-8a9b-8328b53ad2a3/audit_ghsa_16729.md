# [M] aiosmtpd STARTTLS unencrypted commands injection

## Summary
Severity: Medium
Advisory: GHSA-wgjv-9j3q-jhg8
CVE: CVE-2024-34083
CWE: CWE-349
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-wgjv-9j3q-jhg8
Type: github-advisory

## Affected
- PyPI: `aiosmtpd` — affected >=0 <1.4.6

## Details
### Summary
Servers based on aiosmtpd accept extra unencrypted commands after STARTTLS, treating them as if they came from inside the encrypted connection. This could be exploited by a MitM attack.

### References
* [NO STARTTLS: Similar vulnerabilities discovered by previous researchers.](https://nostarttls.secvuln.info/)

## References
- https://github.com/aio-libs/aiosmtpd/security/advisories/GHSA-wgjv-9j3q-jhg8
- https://nvd.nist.gov/vuln/detail/CVE-2024-34083
- https://github.com/aio-libs/aiosmtpd/commit/b3a4a2c6ecfd228856a20d637dc383541fcdbfda
- https://github.com/aio-libs/aiosmtpd
- https://nostarttls.secvuln.info
