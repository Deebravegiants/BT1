# [M] Rancher sends sensitive information to external services through the `/meta/proxy` endpoint

## Summary
Severity: Medium
Advisory: GHSA-mjcp-rj3c-36fr
CVE: CVE-2025-54468
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2025-09-26
Source: https://github.com/advisories/GHSA-mjcp-rj3c-36fr
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.12.0 <2.12.2
- Go: `github.com/rancher/rancher` — affected >=2.11.0 <2.11.6
- Go: `github.com/rancher/rancher` — affected >=2.10.0 <2.10.10
- Go: `github.com/rancher/rancher` — affected >=2.9.0 <2.9.12

## Details
### Impact

A vulnerability has been identified within Rancher Manager whereby `Impersonate-Extra-*` headers are being sent to an external entity, for example `amazonaws.com`, via the `/meta/proxy` Rancher endpoint. These headers may contain identifiable and/or sensitive information e.g. email addresses.

If the authentication provider is configured to have email or other sensitive and/or identifiable information as part of the username and principal ID then when a new cloud credential is being created in Rancher Manager this information is sent to an external entity such as `amazonaws.com`, in case of an AWS cloud credentials, in `Impersonate-Extra-Username` and/or `Impersonate-Extra-Principalid` headers. Please note that neither password, password hashes or Rancher’s related authentication tokens are leaked in those requests.

The entities to which such information is sent to are limited by the whitelisted domains specified in `nodedrivers.management.cattle.io` objects. 

For example, the Amazon EC2 node driver contains the following whitelisted domains:

- `iam.amazonaws.com`
- `iam.us-gov.amazonaws.com`
- `iam.%.amazonaws.com.cn`
- `iam.global.api.aws`
- `ec2.%.amazonaws.com`
- `ec2.%.amazonaws.com.cn`
- `ec2.%.api.aws`
- `eks.%.amazonaws.com`
- `eks.%.amazonaws.com.cn`
- `eks.%.api.aws`
- `kms.%.amazonaws.com`
- `kms.%.amazonaws.com.cn`
- `kms.%.api.aws`

While the DigitalOcean driver contains the following whitelisted domain:

- `api.digitalocean.com`

### Patches

This vulnerability is addressed by filtering all `Impersonate-*` headers from the original request by the `/meta/proxy` endpoint.

Patched versions of Rancher include releases v2.12.2, v2.11.6, v2.10.10, and v2.9.12. 

### Workarounds

There are no known workarounds for this issue.

### References

If you have any questions or comments about this advisory:

- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-mjcp-rj3c-36fr
- https://nvd.nist.gov/vuln/detail/CVE-2025-54468
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2025-54468
- https://github.com/rancher/rancher
- https://pkg.go.dev/vuln/GO-2025-3982
