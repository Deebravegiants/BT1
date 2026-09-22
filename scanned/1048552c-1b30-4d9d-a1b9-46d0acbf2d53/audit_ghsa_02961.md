# [H] Authentication bypass issue in the Operator Console

## Summary
Severity: High
Advisory: GHSA-4999-659w-mq36
CVE: CVE-2021-41266
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2021-11-15
Source: https://github.com/advisories/GHSA-4999-659w-mq36
Type: github-advisory

## Affected
- Go: `github.com/minio/console` — affected >=0 <0.12.3

## Details
During an internal security audit, we detected an authentication bypass issue in the Operator Console when an external IDP is enabled. The security issue has been reported internally. We have not observed this exploit in the wild or reported elsewhere in the community at large. All users are advised to upgrade ASAP.

### Impact

All users on release v0.12.2 and before are affected.

### Patches

This issue was fixed by PR https://github.com/minio/console/pull/1217, users should upgrade to latest release.

### Workarounds

Add `automountServiceAccountToken: false` to the operator-console deployment in Kubernetes so no service account token will get mounted inside the pod, then disable the external identity provider authentication by unset the `CONSOLE_IDP_URL`, `CONSOLE_IDP_CLIENT_ID`, `CONSOLE_IDP_SECRET` and `CONSOLE_IDP_CALLBACK` environment variable and instead use the Kubernetes service account token.

### References

#1217 for more information on the fix and how it was fixed.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [console issues](https://github.com/minio/console/issues)
* Email us at [security@minio.io](mailto:security@minio.io)

## References
- https://github.com/minio/console/security/advisories/GHSA-4999-659w-mq36
- https://nvd.nist.gov/vuln/detail/CVE-2021-41266
- https://github.com/minio/console/pull/1217
- https://github.com/minio/console
