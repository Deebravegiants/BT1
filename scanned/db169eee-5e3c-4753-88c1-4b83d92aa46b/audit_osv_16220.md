# [H] CVE-2019-3779

## Summary
Severity: High
Advisory: CVE-2019-3779
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-08
Source: https://osv.dev/vulnerability/CVE-2019-3779
Type: osv

## Details
Cloud Foundry Container Runtime, versions prior to 0.29.0, deploys Kubernetes clusters utilize the same CA (Certificate Authority) to sign and trust certs for ETCD as used by the Kubernetes API. This could allow a user authenticated with a cluster to request a signed certificate leveraging the Kubernetes CSR capability to obtain a credential that could escalate privilege access to ETCD.

## References
- https://www.cloudfoundry.org/blog/cve-2019-3779
