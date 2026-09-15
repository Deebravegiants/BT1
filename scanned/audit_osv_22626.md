# [H] CVE-2022-34871

## Summary
Severity: High
Advisory: CVE-2022-34871
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-03
Source: https://osv.dev/vulnerability/CVE-2022-34871
Type: osv

## Details
This vulnerability allows remote attackers to escalate privileges on affected installations of Centreon. Authentication is required to exploit this vulnerability. The specific flaw exists within the configuration of poller resources. The issue results from the lack of proper validation of a user-supplied string before using it to construct SQL queries. An attacker can leverage this vulnerability to escalate privileges to the level of an administrator. Was ZDI-CAN-16335.

## References
- https://docs.centreon.com/docs/21.10/releases/centreon-core/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/34xxx/CVE-2022-34871.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-34871
- https://www.zerodayinitiative.com/advisories/ZDI-22-953/
