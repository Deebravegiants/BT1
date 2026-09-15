# [H] Depth counting error in guard() leading to multiple potential security issues in aioxmpp

## Summary
Severity: High
Advisory: GHSA-6m9g-jr8c-cqw3
CVE: CVE-2019-1000007
CWE: CWE-237
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2020-04-29
Source: https://github.com/advisories/GHSA-6m9g-jr8c-cqw3
Type: github-advisory

## Affected
- PyPI: `aioxmpp` — affected >=0 <0.10.3

## Details
### Impact
Possible remote Denial of Service or Data Injection.

### Patches
Patches are available in https://github.com/horazont/aioxmpp/pull/268. They have been backported to the 0.10 release series and 0.10.3 is the first release to contain the fix.

### Workarounds
To make the bug exploitable, an error suppressing ``xso_error_handler`` is required. By not using ``xso_error_handlers`` or not using the suppression function, the vulnerability can be mitigated completely (to our knowledge).

### References
The pull request contains a detailed description: https://github.com/horazont/aioxmpp/pull/268

### For more information
If you have any questions or comments about this advisory:
* [Join our chat](xmpp:aioxmpp@conference.zombofant.net?join)
* Email the maintainer [Jonas Schäfer](mailto:jonas@wielicki.name)

## References
- https://github.com/horazont/aioxmpp/security/advisories/GHSA-6m9g-jr8c-cqw3
- https://nvd.nist.gov/vuln/detail/CVE-2019-1000007
- https://github.com/horazont/aioxmpp/pull/268
- https://github.com/horazont/aioxmpp/commit/29ff0838a40f58efe30a4bbcea95aa8dab7da475
- https://github.com/horazont/aioxmpp/commit/f151f920f439d97d4103fc11057ed6dc34fe98be
- https://github.com/advisories/GHSA-6m9g-jr8c-cqw3
- https://github.com/horazont/aioxmpp
- https://github.com/pypa/advisory-database/tree/main/vulns/aioxmpp/PYSEC-2019-1.yaml
