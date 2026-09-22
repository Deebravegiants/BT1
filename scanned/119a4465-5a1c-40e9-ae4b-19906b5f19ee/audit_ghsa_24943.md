# [H] PyCrypto does not properly reseed PRNG before allowing access

## Summary
Severity: High
Advisory: GHSA-x377-f64p-hf5j
CVE: CVE-2013-1445
CWE: CWE-332
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-x377-f64p-hf5j
Type: github-advisory

## Affected
- PyPI: `pycrypto` — affected >=0 <2.6.1

## Details
The Crypto.Random.atfork function in PyCrypto before 2.6.1 does not properly reseed the pseudo-random number generator (PRNG) before allowing a child process to access it, which makes it easier for context-dependent attackers to obtain sensitive information by leveraging a race condition in which a child process is created and accesses the PRNG within the same rate-limit period as another process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1445
- https://github.com/dlitz/pycrypto/commit/19dcf7b15d61b7dc1a125a367151de40df6ef175
- https://github.com/pycrypto/pycrypto
- https://github.com/pypa/advisory-database/tree/main/vulns/pycrypto/PYSEC-2013-29.yaml
- http://www.debian.org/security/2013/dsa-2781
- http://www.openwall.com/lists/oss-security/2013/10/17/3
