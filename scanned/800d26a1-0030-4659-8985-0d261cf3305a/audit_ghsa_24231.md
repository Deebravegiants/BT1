# [H] Exposure of repository credentials to external third-party sources in Rancher

## Summary
Severity: High
Advisory: GHSA-4fc7-hc63-7fjg
CVE: CVE-2021-36778
CWE: CWE-200, CWE-522, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-4fc7-hc63-7fjg
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.6.0 <2.6.3
- Go: `github.com/rancher/rancher` — affected >=2.5.0 <2.5.12

## Details
### Impact
This issue only happens when the user configures access credentials to a private repository in Rancher inside `Apps & Marketplace > Repositories`. It affects Rancher versions 2.5.0 up to and including 2.5.11 and from 2.6.0 up to and including 2.6.2.

An insufficient check of the same-origin policy when downloading Helm charts from a configured private repository can lead to exposure of the repository credentials to a third-party provider. This exposure happens when the private repository:

1. Does an HTTP redirect to a third-party repository or external storage provider.
2. Downloads an icon resource for the chart hosted on a third-party provider.

The address of the private repository is not leaked, only the credentials are leaked in the HTTP `Authorization` header in base64 format.

With the patched versions, the default behavior now is to only send the private repository credentials when subdomain or domain hostname match when following the redirect or downloading external resources.

### Patches
Patched versions include releases 2.5.12, 2.6.3 and later versions.

### Workarounds
1. Update Rancher to a patched version.
2. Check the Helm charts in your configured private repository for possible redirects to third-party storage, and for Helm chart icons from third-party sources.
3. Evaluate any Helm chart that might lead to the mentioned scenario and change affected credentials if deemed necessary.

### References
Information about the same-origin check and how to disable it is available in Rancher [documentation](https://rancher.com/docs/rancher/v2.6/en/helm-charts/#repositories).

### For more information
If you have any questions or comments about this advisory:
* Reach out to [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
* Open an issue in [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
* Verify our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-4fc7-hc63-7fjg
- https://nvd.nist.gov/vuln/detail/CVE-2021-36778
- https://bugzilla.suse.com/show_bug.cgi?id=1191466
- github.com/rancher/rancher
