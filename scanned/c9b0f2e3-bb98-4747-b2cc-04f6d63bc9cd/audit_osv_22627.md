# [M] CVE-2022-34872

## Summary
Severity: Medium
Advisory: CVE-2022-34872
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-08-03
Source: https://osv.dev/vulnerability/CVE-2022-34872
Type: osv

## Details
This vulnerability allows remote attackers to disclose sensitive information on affected installations of Centreon. Authentication is required to exploit this vulnerability. The specific flaw exists within the processing of Virtual Metrics. The issue results from the lack of proper validation of a user-supplied string before using it to construct SQL queries. An attacker can leverage this vulnerability to disclose stored credentials, leading to further compromise. Was ZDI-CAN-16336.

## References
- https://docs.centreon.com/docs/21.10/releases/centreon-core/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/34xxx/CVE-2022-34872.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-34872
- https://www.zerodayinitiative.com/advisories/ZDI-22-954/
