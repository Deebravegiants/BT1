# [H] CVE-2022-3569

## Summary
Severity: High
Advisory: CVE-2022-3569
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-17
Source: https://osv.dev/vulnerability/CVE-2022-3569
Type: osv

## Details
Due to an issue with incorrect sudo permissions, Zimbra Collaboration Suite (ZCS) suffers from a local privilege escalation issue in versions 9.0.0 and prior, where the 'zimbra' user can effectively coerce postfix into running arbitrary commands as 'root'.

## References
- http://packetstormsecurity.com/files/169430/Zimbra-Privilege-Escalation.html
- https://twitter.com/ldsopreload/status/1580539318879547392
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3569.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3569
- https://github.com/rapid7/metasploit-framework/pull/17141
