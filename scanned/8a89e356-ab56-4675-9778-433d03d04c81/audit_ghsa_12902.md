# [M] scs-library-client may leak user credentials to third-party service via HTTP redirect

## Summary
Severity: Medium
Advisory: GHSA-7p8m-22h4-9pj7
CVE: CVE-2022-23538
CWE: CWE-522, CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-01-20
Source: https://github.com/advisories/GHSA-7p8m-22h4-9pj7
Type: github-advisory

## Affected
- Go: `github.com/sylabs/scs-library-client` — affected >=1.4.0 <1.4.2
- Go: `github.com/sylabs/scs-library-client` — affected >=0 <1.3.4

## Details
### Impact

When the scs-library-client is used to pull a container image, with authentication, the HTTP Authorization header sent by the client to the library service may be incorrectly leaked to an S3 backing storage provider. This occurs in a specific flow, where the library service redirects the client to a backing S3 storage server, to perform a multi-part concurrent download.

Depending on site configuration, the S3 service may be provided by a third party. An attacker with access to the S3 service may be able to extract user credentials, allowing them to impersonate the user.

The vulnerable multi-part concurrent download flow, with redirect to S3, is only used when communicating with a Singularity Enterprise 1.x installation, or third party server implementing this flow.

Interaction with Singularity Enterprise 2.x, and Singularity Container Services (cloud.sylabs.io), does not trigger the vulnerable flow.

We encourage all users to update. Users who interact with a Singularity Enterprise 1.x installation, using a 3rd party S3 storage service, are advised to revoke and recreate their authentication tokens within Singularity Enterprise.

### Patches

The security issue was identified after the integration of a bug-fix commit 68ac4ca into the previously released scs-library-client 1.3.4. This commit fixes the security issue in the 1.3 series.

scs-library-client 1.4.2 contains a fix for the same vulnerability in the 1.4 series, as commit eebd7ca.

### Workarounds

There is no workaround available at this time.

As above, access to Singularity Enterprise 2.x, or Singularity Container Services (cloud.sylabs.io), does not trigger the vulnerable flow.

### References

https://cwe.mitre.org/data/definitions/522.html

## References
- https://github.com/sylabs/scs-library-client/security/advisories/GHSA-7p8m-22h4-9pj7
- https://nvd.nist.gov/vuln/detail/CVE-2022-23538
- https://github.com/sylabs/scs-library-client/commit/68ac4cab5cda0afd8758ff5b5e2e57be6a22fcfa
- https://github.com/sylabs/scs-library-client/commit/b5db2aacba6bf1231f42dd475cc32e6355ab47b2
- https://github.com/sylabs/scs-library-client/commit/eebd7caaab310b1fa803e55b8fc1acd9dcd2d00c
- https://github.com/sylabs/scs-library-client
- https://pkg.go.dev/vuln/GO-2023-1497
