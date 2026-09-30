# [M] Use of a Key Past its Expiration Date in Conduit

## Summary
Severity: Medium
Advisory: CVE-2024-6299
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-06-25
Source: https://osv.dev/vulnerability/CVE-2024-6299
Type: osv

## Details
Lack of consideration of key expiry when validating signatures in Conduit, allowing an attacker which has compromised an expired key to forge requests as the remote server, as well as PDUs with timestamps past the expiry date

## References
- https://conduit.rs/changelog/#v0-8-0-2024-06-12
- https://gitlab.com/famedly/conduit/-/releases/v0.8.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6299.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6299
