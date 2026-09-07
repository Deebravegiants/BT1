# [H] Arbitrary Code Execution in Cookie Serialization

## Summary
Severity: High
Advisory: GHSA-5v4m-c73v-c7gq
CVE: CVE-2017-1000053
CWE: CWE-502
Ecosystem: Hex
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-12
Source: https://github.com/advisories/GHSA-5v4m-c73v-c7gq
Type: github-advisory

## Affected
- Hex: `plug` — affected >=0 <1.0.4
- Hex: `plug` — affected >=1.1.0 <1.1.7
- Hex: `plug` — affected >=1.2.0 <1.2.3
- Hex: `plug` — affected >=1.3.0 <1.3.2

## Details
The default serialization used by Plug session may result in code execution
  in certain situations. Keep in mind, however, the session cookie is signed
  and this attack can only be exploited if the attacker has access to your
  secret key as well as your signing/encryption salts. We recommend users to
  change their secret key base and salts if they suspect they have been leaked,
  regardless of this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000053
- https://elixirforum.com/t/security-releases-for-plug/3913
- https://github.com/elixir-plug/plug
