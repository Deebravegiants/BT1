# [H] Concrete CMS Vulnerable to Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: GHSA-pv2v-6w2v-97x6
CVE: CVE-2026-8135
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-pv2v-6w2v-97x6
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
Concrete CMS 9.5.0 and below is vulnerable to Remote Code Execution  due to insecure deserialization occurring in the ExpressEntryList block controller. An rogue administrator with privileges to add blocks to an area can bypass the intended protection mechanism (_fromCIF === true), which normally restricts malicious inputs over form POST requests, by leveraging the REST API functionality. Because the REST API parses requests using json_decode(), the string "true" is evaluated as a strict PHP Boolean(true).  This bypass allows the attacker to inject a malicious serialized payload  into the block's filterFields database column. The payload will subsequently be executed when the block's data is viewed or edited by an administrator leading to complete server takeover (RCE). Concrete CMS thanks  Nguyễn Văn Thiện https://github.com/Thien225409  for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8135
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms
