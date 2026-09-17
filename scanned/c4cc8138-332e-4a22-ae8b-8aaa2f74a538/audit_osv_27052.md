# [H] Collection of internally resolving IPs

## Summary
Severity: High
Advisory: CVE-2024-0759
CVSS: 7.7 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2024-0759
Type: osv

## Details
Should an instance of AnythingLLM be hosted on an internal network and the attacked be explicitly granted a permission level of manager or admin, they could link-scrape internally resolving IPs of other services that are on the same network as AnythingLLM.

This would require the attacker also be able to guess these internal IPs as `/*` ranging is not possible, but could be brute forced.

There is a duty of care that other services on the same network would not be fully open and accessible via a simple CuRL with zero authentication as it is not possible to set headers or access via the link collector.

## References
- https://huntr.com/bounties/9a978edd-ac94-41fc-8e3e-c35441bdd12b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0759.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0759
- https://github.com/mintplex-labs/anything-llm/commit/0db6c3b2aa1787a7054ffdaba975474f122c20eb
