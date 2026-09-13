# [H] Improper authorization on debug and artifact file downloads

## Summary
Severity: High
Advisory: GHSA-m4hc-m2v6-hfw8
CVE: CVE-2023-36826
CWE: CWE-285
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-25
Source: https://github.com/advisories/GHSA-m4hc-m2v6-hfw8
Type: github-advisory

## Affected
- PyPI: `sentry` — affected >=8.21.0 <23.5.2

## Details
### Impact

An authenticated user can download a debug or artifact bundle from arbitrary organizations and projects with a known bundle ID. The user does not need to be a member of the organization or have permissions on the project.

### Patches

A patch was issued to ensure authorization checks are properly scoped on requests to retrieve debug or artifact bundles. Authenticated users who do not have the necessary permissions on the particular project are no longer able to download them.

**Sentry SaaS users do not need to take any action. [Self-Hosted Sentry](https://github.com/getsentry/self-hosted) users should upgrade to version 23.5.2 or higher.**

### References

- [Restrict file downloads to Project](https://github.com/getsentry/sentry/pull/49680)

## References
- https://github.com/getsentry/sentry/security/advisories/GHSA-m4hc-m2v6-hfw8
- https://nvd.nist.gov/vuln/detail/CVE-2023-36826
- https://github.com/getsentry/sentry/pull/49680
- https://github.com/getsentry/sentry/commit/e932b15435bf36239431eaa3790a6bcfa47046a9
- https://github.com/getsentry/sentry
- https://github.com/pypa/advisory-database/tree/main/vulns/sentry/PYSEC-2023-130.yaml
