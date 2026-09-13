# [C] Rancher doesn't properly sanitize credentials in cluster template answers

## Summary
Severity: Critical
Advisory: GHSA-8w87-58w6-hfv8
CVE: CVE-2021-36783
CWE: CWE-200, CWE-312, CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-8w87-58w6-hfv8
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.5.0 <2.5.13
- Go: `github.com/rancher/rancher` — affected >=2.6.0 <2.6.4

## Details
### Impact

It was discovered that in Rancher versions up to and including 2.5.12 and 2.6.3 there is a failure to properly sanitize credentials in cluster template answers. This failure can lead to plaintext storage and exposure of credentials, passwords and API tokens.

The exposed credentials are visible in Rancher to authenticated `Cluster Owners`, `Cluster Members`, `Project Owners` and `Project Members` on the endpoints `/v1/management.cattle.io.clusters`, `/v3/clusters` and `/k8s/clusters/local/apis/management.cattle.io/v3/clusters`.

Sensitive fields are now stripped from `Clusters` objects before the object is stored. For objects that existed before this security fix, a one-time migration happens on startup.

**Important:**
- It is highly advised to review for potential leaked credentials in this scenario, and to change them if deemed necessary.
- The final impact severity for confidentiality, integrity and availability is dependent on the permissions that the leaked credentials have on their own services.

### Patches
Patched versions include releases 2.5.13, 2.6.4 and later versions.

### Workarounds
Limit access in Rancher to trusted users. There is not a direct mitigation besides upgrading to the patched Rancher versions.

**Important:** It is highly advised to review for potential leaked credentials in this scenario, and to change them if deemed necessary.

### For more information
If you have any questions or comments about this advisory:
* Reach out to [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
* Open an issue in [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
* Verify our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-8w87-58w6-hfv8
- https://nvd.nist.gov/vuln/detail/CVE-2021-36783
- https://bugzilla.suse.com/show_bug.cgi?id=1193990
- https://github.com/rancher/rancher
