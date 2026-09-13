# [H] NHibernate SQL injection vulnerability in discriminator mappings, static fields referenced in HQL, and some utilities

## Summary
Severity: High
Advisory: GHSA-fg4q-ccq8-3r5q
CVE: CVE-2024-39677
CWE: CWE-89
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-07-08
Source: https://github.com/advisories/GHSA-fg4q-ccq8-3r5q
Type: github-advisory

## Affected
- NuGet: `NHibernate` — affected >=0 <5.4.9
- NuGet: `NHibernate` — affected >=5.5.0 <5.5.2

## Details
### Impact
A SQL injection vulnerability exists in some types implementing `ILiteralType.ObjectToSQLString`. Callers of these methods are exposed to the vulnerability, which includes:
 - Mappings using inheritance with discriminator values:
   - The discriminator value could be written in the mapping in a way exploiting the vulnerability of the associated discriminator type, if that type is among the vulnerable ones.
   - The current culture settings for formatting the discriminator value type could be altered in a way resulting into SQL injections with the discriminator values.
 - HQL queries referencing a static field of the application.
 - Users of the `SqlInsertBuilder` and `SqlUpdateBuilder` utilities, calling their `AddColumn` overload taking a literal value. These overloads are unused by NHibernate but could be used by users referencing directly these utilities.
 - Any direct use of the `ObjectToSQLString` methods for building SQL queries on the user side.

### Patches
Releases 5.4.9 and 5.5.2.

### Workarounds
 - Ensure the application does not use the features listed above.
 - For discriminator usages, ensure the discriminator values in the mappings do not contain quotes for string discriminators. Furthermore, for types which `ToString` conversion can be altered to include SQL injections through adequate hacking of the current culture settings, either change for another type, or ensure the used values cannot allow culture exploits, or ensure the application performs sanity checks of the current culture settings. Types sensitive to culture include integers for negative values, dates, times and datetimes, floats and decimals.

### References
 - https://github.com/nhibernate/nhibernate-core/issues/3516
 - https://github.com/nhibernate/nhibernate-core/pull/3517
 - https://github.com/nhibernate/nhibernate-core/pull/3547

## References
- https://github.com/nhibernate/nhibernate-core/security/advisories/GHSA-fg4q-ccq8-3r5q
- https://nvd.nist.gov/vuln/detail/CVE-2024-39677
- https://github.com/nhibernate/nhibernate-core/issues/3516
- https://github.com/nhibernate/nhibernate-core/pull/3517
- https://github.com/nhibernate/nhibernate-core/pull/3547
- https://github.com/nhibernate/nhibernate-core/commit/b4a69d1a5ff5744312478d70308329af496e4ba9
- https://github.com/nhibernate/nhibernate-core
