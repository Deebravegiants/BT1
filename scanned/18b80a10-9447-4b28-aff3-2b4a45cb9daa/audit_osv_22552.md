# [M] Zulip Server insufficient authorization for changing bot roles

## Summary
Severity: Medium
Advisory: CVE-2022-31168
Aliases: GHSA-c3cp-ggg5-9xw5
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2022-07-22
Source: https://osv.dev/vulnerability/CVE-2022-31168
Type: osv

## Details
Zulip is an open source team chat tool. Due to an incorrect authorization check in Zulip Server 5.4 and earlier, a member of an organization could craft an API call that grants organization administrator privileges to one of their bots. The vulnerability is fixed in Zulip Server 5.5. Members who don’t own any bots, and lack permission to create them, can’t exploit the vulnerability. As a workaround for the vulnerability, an organization administrator can restrict the `Who can create bots` permission to administrators only, and change the ownership of existing bots.

## References
- https://github.com/zulip/zulip/releases/tag/5.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31168.json
- https://github.com/zulip/zulip/security/advisories/GHSA-c3cp-ggg5-9xw5
- https://nvd.nist.gov/vuln/detail/CVE-2022-31168
- https://github.com/zulip/zulip/commit/751b2a03e565e9eb02ffe923b7c24ac73d604034
