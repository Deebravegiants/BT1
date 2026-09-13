# [M] CVE-2025-59716

## Summary
Severity: Medium
Advisory: CVE-2025-59716
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-11-05
Source: https://osv.dev/vulnerability/CVE-2025-59716
Type: osv

## Details
ownCloud Guests before 0.12.5 allows unauthenticated user enumeration via the /apps/guests/register/{email}/{token} endpoint. Because of insufficient validation of the supplied token in showPasswordForm, the server responds differently when an e-mail address corresponds to a valid pending guest user rather than a non-existent user.

## References
- https://gist.github.com/thesmartshadow/64ae0449e909174d0479a4f23657147f
- https://marketplace.owncloud.com/apps/guests
- https://yeswehack.com/reports/411806
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59716.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-59716
- https://github.com/owncloud/guests
