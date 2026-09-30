# [M] Multiple vulnerabilities in Canopsis of Capensis

## Summary
Severity: Medium
Advisory: CVE-2023-3196
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-10-03
Source: https://osv.dev/vulnerability/CVE-2023-3196
Type: osv

## Details
This vulnerability could allow an attacker to store a malicious JavaScript payload in the login footer and login page description parameters within the administration panel.

## References
- https://git.canopsis.net/canopsis/canopsis-community/-/blob/develop/community/sources/webcore/src/canopsis-next/src/config.js?ref_type=heads#L38
- https://git.canopsis.net/canopsis/canopsis-community/-/blob/develop/community/sources/webcore/src/canopsis-next/src/helpers/html.js?ref_type=heads
- https://www.incibe.es/en/incibe-cert/notices/aviso/multiple-vulnerabilities-canopsis-capensis
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3196.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3196
