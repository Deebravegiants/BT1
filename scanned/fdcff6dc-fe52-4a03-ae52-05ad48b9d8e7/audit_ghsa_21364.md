# [H] Keylime: unhandled exceptions could lead to invalid attestation states

## Summary
Severity: High
Advisory: GHSA-hff2-x2j9-gxgv
CVE: CVE-2022-3500
CWE: CWE-248
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-28
Source: https://github.com/advisories/GHSA-hff2-x2j9-gxgv
Type: github-advisory

## Affected
- PyPI: `keylime` — affected >=0 <6.5.1

## Details
### Impact

This vulnerability creates a false sense of security for keylime users -- i.e. a user could query keylime and conclude that a parcitular node/agent is correctly attested, while attestations are not in fact taking place.

**Short explanation**: the keylime verifier creates periodic reports on the state of each attested agent. The keylime verifier runs a set of python asynchronous processes to challenge attested nodes and create reports on the outcome. 

The vulnerability consists of the above named python asynchronous processes failing silently, i.e. quitting without leaving behind a database entry, raising an error or producing even a mention of an error in a log. The silent failure can be triggered by a small set of transient network failure conditions; recoverable device driver crashes being one such condition we saw in the wild.

### Patches

The problem is fixed in keylime starting with tag 6.5.1

### Workarounds

This [patch](https://github.com/keylime/keylime/pull/1128/files) can be retroactively applied to any running keylime deployment.
Only running verifiers need to be patched.
After the patch is applied, the keylime verifier needs to be restarted.

### References

The problem, as well as the proposed fix, are described in detail [here](https://github.com/keylime/keylime/pull/1128).
Further details about the system where the bug was found, and the conditions in which the bug was found, are available from @galmasi on demand.

### For more information

If you have any questions or comments about this [advisory](https://github.com/keylime/keylime/security/advisories/GHSA-hff2-x2j9-gxgv), please comment at the bottom of the advisory itself.

## References
- https://github.com/keylime/keylime/security/advisories/GHSA-hff2-x2j9-gxgv
- https://nvd.nist.gov/vuln/detail/CVE-2022-3500
- https://github.com/keylime/keylime/pull/1128
- https://github.com/keylime/keylime/commit/f969d397f92962b553f8c5bcbbeeb3bbdeca9456
- https://access.redhat.com/security/cve/CVE-2022-3500
- https://github.com/keylime/keylime
- https://github.com/pypa/advisory-database/tree/main/vulns/keylime/PYSEC-2022-42995.yaml
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PUTHMDVFNGGVPCNPOGULMJAAFEP7MEXP
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QX4XVCAUFGJ2I2NCTOKONTJGRJB2NBBT
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZQH5CJRX65QYMQN5WGUKKKE3IRJBWG5Z
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PUTHMDVFNGGVPCNPOGULMJAAFEP7MEXP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QX4XVCAUFGJ2I2NCTOKONTJGRJB2NBBT
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZQH5CJRX65QYMQN5WGUKKKE3IRJBWG5Z
