# [M] NeuVector is shipping cryptographic material into its binary

## Summary
Severity: Medium
Advisory: GHSA-h773-7gf7-9m2x
CVE: CVE-2025-54471
CWE: CWE-321
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-21
Source: https://github.com/advisories/GHSA-h773-7gf7-9m2x
Type: github-advisory

## Affected
- Go: `github.com/neuvector/neuvector` — affected >=5.3.0 <5.4.7
- Go: `github.com/neuvector/neuvector` — affected >=0.0.0-20230727023453-1c4957d53911 <0.0.0-20251020133207-084a437033b4

## Details
### Impact
NeuVector used a hard-coded cryptographic key embedded in the source code. At compilation time, the key value was replaced with the secret key value and used to encrypt sensitive configurations  when NeuVector stores the data.

In the patched version, NeuVector leverages the Kubernetes secret `neuvector-store-secret` in `neuvector` namespace to dynamically generate cryptographically secure random keys. This approach removes the reliance on static key values and ensures that encryption keys are managed securely within Kubernetes.

During rolling upgrade or restoring from persistent storage, the NeuVector controller checks each encrypted configured field. If a sensitive field in the configuration is found to be encrypted by the default encryption key, it’s decrypted with the default encryption key and then re-encrypted with the new dynamic encryption key.

If the NeuVector controller does not have the correct RBAC for accessing the new secret, it writes this error log : 
`Required Kubernetes RBAC for secrets are not found` and exits.

The device encryption key is rotated every 3 months. For details, please refer to this [Rotating Self-Signed Certificate](https://open-docs.neuvector.com/configuration/console/certrotate) documentation.

### Patches
Patched versions include release **v5.4.7** and above.

### Workarounds
There is no workaround for this issue. Users are recommended to upgrade, as soon as possible, to a version of NeuVector that contains the fix.

### References
If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [NeuVector](https://github.com/neuvector/neuvector/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-neuvector/support-matrix/all-supported-versions/neuvector-v-all-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/#suse-security).

## References
- https://github.com/neuvector/neuvector/security/advisories/GHSA-h773-7gf7-9m2x
- https://nvd.nist.gov/vuln/detail/CVE-2025-54471
- https://github.com/neuvector/neuvector/commit/084a437033b491eeea11bdba1a09dd84ed12ea88
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2025-54471
- https://github.com/neuvector/neuvector
