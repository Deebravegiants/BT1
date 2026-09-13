# [M] FastAsyncWorldEdit vulnerable to Uncontrolled Resource Consumption

## Summary
Severity: Medium
Advisory: GHSA-whj9-m24x-qhhp
CVE: CVE-2023-35925
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-22
Source: https://github.com/advisories/GHSA-whj9-m24x-qhhp
Type: github-advisory

## Affected
- Maven: `com.fastasyncworldedit:FastAsyncWorldEdit-Core` — affected >=0 <2.6.3
- Maven: `com.fastasyncworldedit:FastAsyncWorldEdit-Bukkit` — affected >=0 <2.6.3

## Details
### Coordinated Disclosure Timeline

- 10.06.2023: Issue reported to IntellectualSites
- 11.06.2023: Issue is acknowledged
- 12.06.2023: Issue has been fixed
- 22.06.2023: Advisory has been published

### Impacted version range

Before 2.6.3

### Details

#### Proof of Concept

As a user, do the following:

1. Select position 1 via `//pos1`
2. Select position 2 adding the "Infinity" keyword via `//pos2 Infinity`
3. Execute any further operation.

The steps 1 and 2 are interchangeable.

#### Impact

Such a task has a possibility of bringing the performing server down.

#### CVE

- CVE-2023-35925

#### Credit

This issue was discovered and [reported](https://github.com/IntellectualSites/.github/blob/main/SECURITY.md) by @SuperMonis.

### Solution

On June 12, 2023, a patch, https://github.com/IntellectualSites/FastAsyncWorldEdit/pull/2285, has been merged addressing the vulnerability.
We strongly recommend users to update their version of FastAsyncWorldEdit to 2.6.3 as soon as possible.

### Workarounds

There is no direct mitigation besides updating FastAsyncWorldEdit to a patched version.

### Additional Information

Users with access to the `logs/` folder or shell access on their server can try to identify possible abuses of this issue by going through the logs.
To sieve through the data, you can use the regex query `\/\/pos[12] Infinity`, then investigate all log entries that return results.

### Disclosure Policy

If you discover a security vulnerability within our software, please report the issue according to our [vulnerability disclosure policy](https://github.com/IntellectualSites/.github/blob/main/SECURITY.md).

## References
- https://github.com/IntellectualSites/FastAsyncWorldEdit/security/advisories/GHSA-whj9-m24x-qhhp
- https://nvd.nist.gov/vuln/detail/CVE-2023-35925
- https://github.com/IntellectualSites/FastAsyncWorldEdit/pull/2285
- https://github.com/IntellectualSites/FastAsyncWorldEdit
- https://github.com/IntellectualSites/FastAsyncWorldEdit/releases/tag/2.6.3
