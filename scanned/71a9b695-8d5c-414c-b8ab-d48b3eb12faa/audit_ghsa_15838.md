# [H] Waitress vulnerable to DoS leading to high CPU usage/resource exhaustion

## Summary
Severity: High
Advisory: GHSA-3f84-rpwh-47g6
CVE: CVE-2024-49769
CWE: CWE-772
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-29
Source: https://github.com/advisories/GHSA-3f84-rpwh-47g6
Type: github-advisory

## Affected
- PyPI: `waitress` — affected >=0 <3.0.1

## Details
### Impact

When a remote client closes the connection before waitress has had the opportunity to call `getpeername()` waitress won't correctly clean up the connection leading to the main thread attempting to write to a socket that no longer exists, but not removing it from the list of sockets to attempt to process. This leads to a busy-loop calling the write function.

A remote attacker could run waitress out of available sockets with very little resources required.

### Patches

Waitress 3.0.1 contains fixes that remove the race condition.

### Workarounds

No work-around.

### References

- https://github.com/Pylons/waitress/issues/418
- https://github.com/Pylons/waitress/pull/435

## References
- https://github.com/Pylons/waitress/security/advisories/GHSA-3f84-rpwh-47g6
- https://nvd.nist.gov/vuln/detail/CVE-2024-49769
- https://github.com/Pylons/waitress/issues/418
- https://github.com/Pylons/waitress/pull/435
- https://github.com/Pylons/waitress/commit/1ae4e894c9f76543bee06584001583fc6fa8c95c
- https://github.com/Pylons/waitress
- https://github.com/pypa/advisory-database/tree/main/vulns/waitress/PYSEC-2024-211.yaml
- https://lists.debian.org/debian-lts-announce/2024/11/msg00012.html
