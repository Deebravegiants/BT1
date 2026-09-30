# [H] OpenSignLabs OpenSign - Information Disclosure

## Summary
Severity: High
Advisory: CVE-2026-72548
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72548
Type: osv

## Details
An information disclosure vulnerability in OpenSignLabs OpenSign through 2.37.0 allows unauthenticated remote attackers to retrieve any organisation tenant record via the gettenant Parse cloud function. The function accepts a contactId parameter and returns the full tenant record without authentication or authorization checks. An attacker can enumerate and disclose tenant configuration data for any organisation in the system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72548.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72548
- https://github.com/OpenSignLabs/OpenSign
