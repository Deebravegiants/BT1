# [H] Private Field data leak

## Summary
Severity: High
Advisory: GHSA-27g8-r9vw-765x
CVE: CVE-2021-32624
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-27
Source: https://github.com/advisories/GHSA-27g8-r9vw-765x
Type: github-advisory

## Affected
- npm: `@keystonejs/keystone` — affected >=0

## Details
This security advisory relates to a newly discovered capability in our query infrastructure to directly or indirectly expose the values of private fields, bypassing the configured access control.

This is an access control related oracle attack in that the attack method guides an attacker during their attempt to reveal information they do not have access to. The complexity of completing the attack is limited by some length-dependent behaviors and the fidelity of the exposed information.

### Impact

Under some circumstances, field values or field value meta data can be determined, despite the field or list having `read` access control configured. If you use private fields or lists, you may be impacted.

### Patches

None, at this time

### Workarounds

None, at this time

### References

None

### For more information

For the protection of the community and private deployments, we think that the best course of action will be to not disclose further details on any open GitHub issues related to this advisory until a hot-fix or work-around has been deployed or published.

If needed, you can email us at keystone@thinkmill.com.au

## References
- https://github.com/keystonejs/keystone-5/security/advisories/GHSA-27g8-r9vw-765x
- https://nvd.nist.gov/vuln/detail/CVE-2021-32624
