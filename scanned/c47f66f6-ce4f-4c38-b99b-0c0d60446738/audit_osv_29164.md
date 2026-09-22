# [M] Unintentional exposure of environment variables to subprocesses in sentry-sdk

## Summary
Severity: Medium
Advisory: CVE-2024-40647
Aliases: GHSA-g92j-qhmh-64v2, PYSEC-2026-1917
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:N/A:N)
Published: 2024-07-18
Source: https://osv.dev/vulnerability/CVE-2024-40647
Type: osv

## Details
sentry-sdk is the official Python SDK for Sentry.io. A bug in Sentry's Python SDK < 2.8.0 allows the environment variables to be passed to subprocesses despite the `env={}` setting. In Python's `subprocess` calls, all environment variables are passed to subprocesses by default. However, if you specifically do not want them to be passed to subprocesses, you may use `env` argument in `subprocess` calls. Due to the bug in Sentry SDK, with the Stdlib integration enabled (which is enabled by default), this expectation is not fulfilled, and all environment variables are being passed to subprocesses instead. The issue has been patched in pull request #3251 and is included in sentry-sdk==2.8.0. We strongly recommend upgrading to the latest SDK version. However, if it's not possible, and if passing environment variables to child processes poses a security risk for you, you can disable all default integrations.

## References
- https://docs.python.org/3/library/subprocess.html
- https://docs.sentry.io/platforms/python/integrations/default-integrations
- https://docs.sentry.io/platforms/python/integrations/default-integrations/#stdlib
- https://github.com/getsentry/sentry-python/releases/tag/2.8.0
- https://lists.debian.org/debian-lts-announce/2026/06/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40647.json
- https://github.com/getsentry/sentry-python/security/advisories/GHSA-g92j-qhmh-64v2
- https://nvd.nist.gov/vuln/detail/CVE-2024-40647
- https://github.com/getsentry/sentry-python/commit/763e40aa4cb57ecced467f48f78f335c87e9bdff
- https://github.com/getsentry/sentry-python/pull/3251
