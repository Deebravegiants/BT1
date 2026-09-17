# [M] Cipher.update_into can corrupt memory if passed an immutable python object as the outbuf

## Summary
Severity: Medium
Advisory: GHSA-w7pp-m8wf-vj6r
CVE: CVE-2023-23931
CWE: CWE-754
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2023-02-07
Source: https://github.com/advisories/GHSA-w7pp-m8wf-vj6r
Type: github-advisory

## Affected
- PyPI: `cryptography` — affected >=1.8 <39.0.1

## Details
Previously, `Cipher.update_into` would accept Python objects which implement the buffer protocol, but provide only immutable buffers:

```pycon
>>> outbuf = b"\x00" * 32
>>> c = ciphers.Cipher(AES(b"\x00" * 32), modes.ECB()).encryptor()
>>> c.update_into(b"\x00" * 16, outbuf)
16
>>> outbuf
b'\xdc\x95\xc0x\xa2@\x89\x89\xadH\xa2\x14\x92\x84 \x87\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
```

This would allow immutable objects (such as `bytes`) to be mutated, thus violating fundamental rules of Python. This is a soundness bug -- it allows programmers to misuse an API, it cannot be exploited by attacker controlled data alone.

This now correctly raises an exception.

This issue has been present since `update_into` was originally introduced in cryptography 1.8.

## References
- https://github.com/pyca/cryptography/security/advisories/GHSA-w7pp-m8wf-vj6r
- https://nvd.nist.gov/vuln/detail/CVE-2023-23931
- https://github.com/pyca/cryptography/pull/8230
- https://github.com/pyca/cryptography/commit/d6951dca25de45abd52da51b608055371fbcde4e
- https://github.com/pyca/cryptography
- https://github.com/pypa/advisory-database/tree/main/vulns/cryptography/PYSEC-2023-11.yaml
- https://lists.debian.org/debian-lts-announce/2024/10/msg00012.html
- https://security.netapp.com/advisory/ntap-20230324-0007
