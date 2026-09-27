# [H] Improper Verification of Cryptographic Signature in fastecdsa

## Summary
Severity: High
Advisory: GHSA-56wv-2wr9-3h9r
CVE: CVE-2020-12607
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-56wv-2wr9-3h9r
Type: github-advisory

## Affected
- PyPI: `fastecdsa` — affected >=0 <2.1.2

## Details
An issue was discovered in fastecdsa before 2.1.2. When using the NIST P-256 curve in the ECDSA implementation, the point at infinity is mishandled. This means that for an extreme value in k and s<sup>-1</sup>, the signature verification fails even if the signature is correct. This behavior is not solely a usability problem. There are some threat models where an attacker can benefit by successfully guessing users for whom signature verification will fail.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12607
- https://github.com/AntonKueltz/fastecdsa/issues/52
- https://github.com/AntonKueltz/fastecdsa/commit/4a16daeaf139be20654ef58a9fe4c79dc030458c
- https://github.com/AntonKueltz/fastecdsa/commit/7b64e3efaa806b4daaf73bb5172af3581812f8de
- https://github.com/AntonKueltz/fastecdsa/commit/e592f106edd5acf6dacedfab2ad16fe6c735c9d1
- https://github.com/AntonKueltz/fastecdsa
- https://github.com/advisories/GHSA-56wv-2wr9-3h9r
- https://github.com/pypa/advisory-database/tree/main/vulns/fastecdsa/PYSEC-2020-42.yaml
