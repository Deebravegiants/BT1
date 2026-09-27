# [H] CVE-2022-42428

## Summary
Severity: High
Advisory: CVE-2022-42428
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-29
Source: https://osv.dev/vulnerability/CVE-2022-42428
Type: osv

## Details
This vulnerability allows remote attackers to escalate privileges on affected installations of Centreon. Authentication is required to exploit this vulnerability. The specific flaw exists within the handling of requests to modify poller broker configuration. The issue results from the lack of proper validation of a user-supplied string before using it to construct SQL queries. An attacker can leverage this vulnerability to escalate privileges to the level of an administrator. Was ZDI-CAN-18410.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/42xxx/CVE-2022-42428.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-42428
- https://www.zerodayinitiative.com/advisories/ZDI-22-1399/
