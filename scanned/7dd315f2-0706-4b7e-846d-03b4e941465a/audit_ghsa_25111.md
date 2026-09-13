# [C] TeamPass Storing Passwords in a Recoverable Format vulnerability

## Summary
Severity: Critical
Advisory: GHSA-q9qr-h33g-fw3j
CVE: CVE-2019-1000001
CWE: CWE-522
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-q9qr-h33g-fw3j
Type: github-advisory

## Affected
- Packagist: `nilsteampassnet/teampass` — affected >=0

## Details
TeamPass version 2.1.27 and earlier contains a Storing Passwords in a Recoverable Format vulnerability in Shared password vaults that can result in all shared passwords are recoverable server side. This attack appears to be exploitable via any vulnerability that can bypass authentication or role assignment and can lead to shared password leakage.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1000001
- https://github.com/nilsteampassnet/TeamPass/issues/2495
- https://github.com/nilsteampassnet/TeamPass
