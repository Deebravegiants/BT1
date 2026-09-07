# [H] Null Byte Injection in Plug.Static

## Summary
Severity: High
Advisory: GHSA-2q6v-32mr-8p8x
CVE: CVE-2017-1000052
CWE: CWE-74
Ecosystem: Hex
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-12
Source: https://github.com/advisories/GHSA-2q6v-32mr-8p8x
Type: github-advisory

## Affected
- Hex: `plug` — affected >=0 <1.0.4
- Hex: `plug` — affected >=1.1.0 <1.1.7
- Hex: `plug` — affected >=1.2.0 <1.2.3
- Hex: `plug` — affected >=1.3.0 <1.3.2

## Details
Plug.Static is used for serving static assets, and is vulnerable to null
  byte injection. If file upload functionality is provided, this can allow
  users to bypass filetype restrictions.
  We recommend all applications that provide file upload functionality and
  serve those uploaded files locally with Plug.Static to upgrade immediately
  or include the fix below. If uploaded files are rather stored and served
  from S3 or any other cloud storage, you are not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000052
- https://elixirforum.com/t/security-releases-for-plug/3913
- https://github.com/elixir-plug/plug
