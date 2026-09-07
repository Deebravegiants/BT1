# [C] Improper Verification of Cryptographic Signature in Pure-Python ECDSA

## Summary
Severity: Critical
Advisory: GHSA-8qxj-f9rh-9fg2
CVE: CVE-2019-14859
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2020-04-01
Source: https://github.com/advisories/GHSA-8qxj-f9rh-9fg2
Type: github-advisory

## Affected
- PyPI: `ecdsa` — affected >=0 <0.13.3

## Details
A flaw was found in all python-ecdsa versions before 0.13.3, where it did not correctly verify whether signatures used DER encoding. Without this verification, a malformed signature could be accepted, making the signature malleable. Without proper verification, an attacker could use a malleable signature to create false transactions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14859
- https://github.com/warner/python-ecdsa/issues/114
- https://github.com/warner/python-ecdsa/pull/115
- https://github.com/tlsfuzzer/python-ecdsa/commit/3427fa29f319b27898a28601955807abb44c0830
- https://github.com/tlsfuzzer/python-ecdsa/commit/9080d1d5ac533da0de00466aaffb49bee808bb4e
- https://github.com/tlsfuzzer/python-ecdsa/commit/b0ea52bb3aa9a16c9a4a91fdc0041edbfed10b31
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14859
- https://github.com/advisories/GHSA-8qxj-f9rh-9fg2
- https://github.com/pypa/advisory-database/tree/main/vulns/ecdsa/PYSEC-2020-163.yaml
- https://github.com/warner/python-ecdsa
- https://github.com/warner/python-ecdsa/releases/tag/python-ecdsa-0.13.3
- https://pypi.org/project/ecdsa/0.13.3
