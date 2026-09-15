# [M] Insecure Temporary File in RESTEasy

## Summary
Severity: Medium
Advisory: GHSA-2c6g-pfx3-w7h8
CVE: CVE-2023-0482
CWE: CWE-378
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-01-15
Source: https://github.com/advisories/GHSA-2c6g-pfx3-w7h8
Type: github-advisory

## Affected
- Maven: `org.jboss.resteasy:resteasy-core` — affected >=6.0.0.Beta1 <6.2.3.Final
- Maven: `org.jboss.resteasy:resteasy-core` — affected >=5.0.0.Alpha1 <5.0.6.Final
- Maven: `org.jboss.resteasy:resteasy-core` — affected >=4.0.0.Beta1 <4.7.8.Final
- Maven: `org.jboss.resteasy:resteasy-multipart-provider` — affected >=6.0.0.Beta1 <6.2.3.Final
- Maven: `org.jboss.resteasy:resteasy-multipart-provider` — affected >=5.0.0.Alpha1 <5.0.6.Final
- Maven: `org.jboss.resteasy:resteasy-multipart-provider` — affected >=4.0.0.Beta1 <4.7.8.Final
- Maven: `org.jboss.resteasy:resteasy-multipart-provider` — affected >=0 <3.15.5.Final
- Maven: `org.jboss.resteasy:resteasy-core` — affected >=0 <3.15.5.Final

## Details
### Impact
In RESTEasy the insecure `File.createTempFile()` is used in the `DataSourceProvider`, `FileProvider` and `Mime4JWorkaround` classes which creates temp files with insecure permissions that could be read by a local user.

### Patches
Fixed in the following pull requests:

* https://github.com/resteasy/resteasy/pull/3409 (7.0.0.Alpha1)
* https://github.com/resteasy/resteasy/pull/3423 (6.2.3.Final)
* https://github.com/resteasy/resteasy/pull/3412 (5.0.6.Final)
* https://github.com/resteasy/resteasy/pull/3413 (4.7.8.Final)
* https://github.com/resteasy/resteasy/pull/3410 (3.15.5.Final)

### Workarounds
There is no workaround for this issue.

### References
* https://nvd.nist.gov/vuln/detail/CVE-2023-0482
* https://bugzilla.redhat.com/show_bug.cgi?id=2166004
* https://github.com/advisories/GHSA-jrmh-v64j-mjm9

## References
- https://github.com/resteasy/resteasy/security/advisories/GHSA-2c6g-pfx3-w7h8
- https://nvd.nist.gov/vuln/detail/CVE-2023-0482
- https://github.com/resteasy/resteasy/pull/3409
- https://github.com/resteasy/resteasy/pull/3409/commits/807d7456f2137cde8ef7c316707211bf4e542d56
- https://github.com/resteasy/resteasy/pull/3410
- https://github.com/resteasy/resteasy/pull/3412
- https://github.com/resteasy/resteasy/pull/3413
- https://github.com/resteasy/resteasy/pull/3423
- https://bugzilla.redhat.com/show_bug.cgi?id=2166004
- https://github.com/orgs/resteasy/discussions/3415
- https://github.com/orgs/resteasy/discussions/3504
- https://github.com/orgs/resteasy/discussions/3506
- https://github.com/resteasy/resteasy
- https://issues.redhat.com/browse/RESTEASY-3286
- https://security.netapp.com/advisory/ntap-20230427-0001
