# [H] ActivityWatch vulnerable to DNS rebinding attack

## Summary
Severity: High
Advisory: CVE-2022-31149
Aliases: GHSA-v9fg-6g9j-h4x4
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-09-07
Source: https://osv.dev/vulnerability/CVE-2022-31149
Type: osv

## Details
ActivityWatch open-source automated time tracker. Versions prior to 0.12.0b2 are vulnerable to DNS rebinding attacks. This vulnerability impacts everyone running ActivityWatch and gives the attacker full access to the ActivityWatch REST API. Users should upgrade to v0.12.0b2 or later to receive a patch. As a workaround, block DNS lookups that resolve to 127.0.0.1.

## References
- https://gist.github.com/zozs/fdebbce75fc8538c15851b46db944a16
- https://github.com/ActivityWatch/activitywatch/discussions/778
- https://github.com/ActivityWatch/activitywatch/security/advisories/GHSA-v9fg-6g9j-h4x4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31149.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-31149
