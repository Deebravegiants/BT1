# [M] secrets-store-csi-driver discloses service account tokens in logs

## Summary
Severity: Medium
Advisory: GHSA-g82w-58jf-gcxx
CVE: CVE-2023-2878
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-05-26
Source: https://github.com/advisories/GHSA-g82w-58jf-gcxx
Type: github-advisory

## Affected
- Go: `sigs.k8s.io/secrets-store-csi-driver` — affected >=0 <1.3.3

## Details
A security issue was discovered in secrets-store-csi-driver where an actor with access to the driver logs could observe service account tokens.  These tokens could then potentially be exchanged with external cloud providers to access secrets stored in cloud vault solutions.  Tokens are only logged when [TokenRequests is configured in the CSIDriver object](https://kubernetes-csi.github.io/docs/token-requests.html) and the driver is set to run at log level 2 or greater via the -v flag.


This issue has been rated MEDIUM [CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N](https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N) (6.5), and assigned CVE-2023-2878


### Am I vulnerable?

You may be vulnerable if [TokenRequests is configured in the CSIDriver object](https://kubernetes-csi.github.io/docs/token-requests.html) and the driver is set to run at log level 2 or greater via the -v flag.


To check if token requests are configured, run the following command:

```bash
kubectl get csidriver secrets-store.csi.k8s.io -o jsonpath="{.spec.tokenRequests}"
```

To check if tokens are being logged, examine the secrets-store container log:

```bash
kubectl logs -l app=secrets-store-csi-driver -c secrets-store -f | grep --line-buffered "csi.storage.k8s.io/serviceAccount.tokens"
```

### Affected Versions

- secrets-store-csi-driver < 1.3.3


### How do I mitigate this vulnerability?

Prior to upgrading, this vulnerability can be mitigated by running secrets-store-csi-driver at log level 0 or 1 via the -v flag.


### Fixed Versions


- secrets-store-csi-driver >= 1.3.3


To upgrade, refer to the documentation: https://secrets-store-csi-driver.sigs.k8s.io/getting-started/upgrades.html#upgrades


### Detection


Examine cloud provider logs for unexpected token exchanges, as well as unexpected access to cloud vault secrets.


If you find evidence that this vulnerability has been exploited, please contact [security@kubernetes.io](https://groups.google.com/)

## References
- https://github.com/kubernetes-sigs/secrets-store-csi-driver/security/advisories/GHSA-g82w-58jf-gcxx
- https://nvd.nist.gov/vuln/detail/CVE-2023-2878
- https://github.com/kubernetes/kubernetes/issues/118419
- https://github.com/kubernetes-sigs/secrets-store-csi-driver
- https://github.com/kubernetes-sigs/secrets-store-csi-driver/releases/tag/v1.3.3
- https://groups.google.com/g/kubernetes-security-announce/c/5K8ghQHBDdQ/m/Udee6YUgAAAJ
- https://security.netapp.com/advisory/ntap-20230814-0003
