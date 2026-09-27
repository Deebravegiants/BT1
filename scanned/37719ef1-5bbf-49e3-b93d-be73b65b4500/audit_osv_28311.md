# [C] GPT Academic: Pickle deserializing cookies may pose RCE risk

## Summary
Severity: Critical
Advisory: CVE-2024-31224
Aliases: GHSA-jcjc-89wr-vv7g
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-08
Source: https://osv.dev/vulnerability/CVE-2024-31224
Type: osv

## Details
GPT Academic provides interactive interfaces for large language models. A vulnerability was found in gpt_academic versions 3.64 through 3.73. The server deserializes untrustworthy data from the client, which may risk remote code execution. Any device that exposes the GPT Academic service to the Internet is vulnerable. Version 3.74 contains a patch for the issue. There are no known workarounds aside from upgrading to a patched version.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31224.json
- https://github.com/binary-husky/gpt_academic/security/advisories/GHSA-jcjc-89wr-vv7g
- https://nvd.nist.gov/vuln/detail/CVE-2024-31224
- https://github.com/binary-husky/gpt_academic/commit/8af6c0cab6d96f5c4520bec85b24802e6e823f35
- https://github.com/binary-husky/gpt_academic/pull/1648
