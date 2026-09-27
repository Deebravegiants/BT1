# [C] CVE-2021-32654

## Summary
Severity: Critical
Advisory: CVE-2021-32654
Aliases: GHSA-jf9h-v24c-22g5
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-06-01
Source: https://osv.dev/vulnerability/CVE-2021-32654
Type: osv

## Details
Nextcloud Server is a Nextcloud package that handles data storage. In versions prior to 19.0.11, 20.0.10, and 21.0.2, an attacker is able to receive write/read privileges on any Federated File Share. Since public links can be added as federated file share, this can also be exploited on any public link. Users can upgrade to patched versions (19.0.11, 20.0.10 or 21.0.2) or, as a workaround, disable federated file sharing.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-jf9h-v24c-22g5
- https://security.gentoo.org/glsa/202208-17
- https://hackerone.com/reports/1170024
