# [H] Nautobot: GitRepository.current_head field should not be writable through REST API

## Summary
Severity: High
Advisory: GHSA-p3hx-pwf3-j8wr
CVE: CVE-2026-44798
CWE: CWE-471, CWE-749
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-p3hx-pwf3-j8wr
Type: github-advisory

## Affected
- PyPI: `nautobot` — affected >=3.0.0a2 <3.1.2
- PyPI: `nautobot` — affected >=0 <2.4.33

## Details
### Impact

A user with access to add/change a GitRepository record could use the REST API to directly set the `current_head` field on the record, which was not intended to be user-editable. Doing so could cause Nautobot's local clone(s) of the relevant repository to checkout a commit other than the latest commit on the specified `branch` (resulting in misleading state), or potentially to be unable to make use of the repository at all (until manually remediated) due to the `current_head` pointing to a nonexistent commit hash or malformed value.

### Patches

The issue has been remediated in Nautobot v2.4.33 and 3.1.2.


### Workarounds

Note that many of the same end-result symptoms could be caused by a user with the same level of access simply changing the `branch` or `remote_url` of a GitRepository rather than crafting the `current_head`. Administrators are encouraged to carefully review which users are granted permissions to create and modify GitRepository records.


### References

- 2.4.33 (<a href="https://github.com/nautobot/nautobot/commit/9deddfc91ad9260ad17b5e20084e9e2d15be3609">patch</a>)
- 3.1.2 (<a href="https://github.com/nautobot/nautobot/commit/c46f97040b2bde4320be36b23577f19a8bcbd8c3">patch</a>)

## References
- https://github.com/nautobot/nautobot/security/advisories/GHSA-p3hx-pwf3-j8wr
- https://nvd.nist.gov/vuln/detail/CVE-2026-44798
- https://github.com/nautobot/nautobot/commit/9deddfc91ad9260ad17b5e20084e9e2d15be3609
- https://github.com/nautobot/nautobot/commit/c46f97040b2bde4320be36b23577f19a8bcbd8c3
- https://github.com/nautobot/nautobot
- https://github.com/nautobot/nautobot/releases/tag/v2.4.33
- https://github.com/nautobot/nautobot/releases/tag/v3.1.2
