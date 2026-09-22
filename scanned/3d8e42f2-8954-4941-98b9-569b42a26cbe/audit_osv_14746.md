# [M] CVE-2019-11252

## Summary
Severity: Medium
Advisory: CVE-2019-11252
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-07-23
Source: https://osv.dev/vulnerability/CVE-2019-11252
Type: osv

## Details
The Kubernetes kube-controller-manager in versions v1.0-v1.17 is vulnerable to a credential leakage via error messages in mount failure logs and events for AzureFile and CephFS volumes.

## References
- https://github.com/kubernetes/kubernetes/pull/88684
