# [M] Possible leak of key's raw field if declared length is incorrect

## Summary
Severity: Medium
Advisory: GHSA-hm37-9xh2-q499
CVE: CVE-2022-31124
CWE: CWE-209
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-07-06
Source: https://github.com/advisories/GHSA-hm37-9xh2-q499
Type: github-advisory

## Affected
- PyPI: `openssh-key-parser` — affected >=0 <0.0.6

## Details
### Impact
If a field of a key is shorter than it is declared to be, the parser raises an error with a message containing the raw field value. An attacker able to modify the declared length of a key's sensitive field can thus expose the raw value of that field.

### Patches
Upgrade to version 0.0.6, which no longer includes the raw field value in the error message.

### Workarounds
N/A

### References
N/A

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [openssh_key_parser](https://github.com/scottcwang/openssh_key_parser)

## References
- https://github.com/scottcwang/openssh_key_parser/security/advisories/GHSA-hm37-9xh2-q499
- https://nvd.nist.gov/vuln/detail/CVE-2022-31124
- https://github.com/scottcwang/openssh_key_parser/pull/5
- https://github.com/scottcwang/openssh_key_parser/commit/26e0a471e9fdb23e635bc3014cf4cbd2323a08d3
- https://github.com/scottcwang/openssh_key_parser/commit/274447f91b4037b7050ae634879b657554523b39
- https://github.com/scottcwang/openssh_key_parser/commit/d5b53b4b7e76c5b666fc657019dbf864fb04076c
- https://github.com/pypa/advisory-database/tree/main/vulns/openssh-key-parser/PYSEC-2022-233.yaml
- https://github.com/scottcwang/openssh_key_parser
