# [H] Rack has possible DoS Vulnerability in Multipart MIME parsing

## Summary
Severity: High
Advisory: GHSA-3h57-hmj3-gj3p
CVE: CVE-2023-27530
CWE: CWE-400, CWE-770
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-08
Source: https://github.com/advisories/GHSA-3h57-hmj3-gj3p
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <2.0.9.3
- RubyGems: `rack` — affected >=2.1.0 <2.1.4.3
- RubyGems: `rack` — affected >=2.2.0 <2.2.6.3
- RubyGems: `rack` — affected >=3.0.0 <3.0.4.2

## Details
There is a possible DoS vulnerability in the Multipart MIME parsing code in Rack. This vulnerability has been assigned the CVE identifier CVE-2023-27530.

Versions Affected: All. Not affected: None Fixed Versions: 3.0.4.2, 2.2.6.3, 2.1.4.3, 2.0.9.3

# Impact
The Multipart MIME parsing code in Rack limits the number of file parts, but does not limit the total number of parts that can be uploaded. Carefully crafted requests can abuse this and cause multipart parsing to take longer than expected.

All users running an affected release should either upgrade or use one of the workarounds immediately.

# Workarounds
A proxy can be configured to limit the POST body size which will mitigate this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27530
- https://discuss.rubyonrails.org/t/cve-2023-27530-possible-dos-vulnerability-in-multipart-mime-parsing/82388
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2023-27530.yml
- https://lists.debian.org/debian-lts-announce/2023/04/msg00017.html
- https://security.netapp.com/advisory/ntap-20231208-0015
- https://www.debian.org/security/2023/dsa-5530
