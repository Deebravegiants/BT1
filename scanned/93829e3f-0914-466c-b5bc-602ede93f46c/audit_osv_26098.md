# [M] CVE-2023-50966

## Summary
Severity: Medium
Advisory: CVE-2023-50966
Aliases: GHSA-9mg4-v392-8j68
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-03-19
Source: https://osv.dev/vulnerability/CVE-2023-50966
Type: osv

## Details
erlang-jose (aka JOSE for Erlang and Elixir) through 1.11.6 allow attackers to cause a denial of service (CPU consumption) via a large p2c (aka PBES2 Count) value in a JOSE header.

## References
- https://github.com/P3ngu1nW/CVE_Request/blob/main/erlang-jose.md
- https://hexdocs.pm/jose/JOSE.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50966.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-50966
- https://github.com/potatosalad/erlang-jose
