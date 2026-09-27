# [M] CVE-2022-40816

## Summary
Severity: Medium
Advisory: CVE-2022-40816
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-27
Source: https://osv.dev/vulnerability/CVE-2022-40816
Type: osv

## Details
Zammad 5.2.1 is vulnerable to Incorrect Access Control. Zammad's asset handling mechanism has logic to ensure that customer users are not able to see personal information of other users. This logic was not effective when used through a web socket connection, so that a logged-in attacker would be able to fetch personal data of other users by querying the Zammad API. This issue is fixed in , 5.2.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/40xxx/CVE-2022-40816.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-40816
- https://zammad.com/de/advisories/zaa-2022-09
