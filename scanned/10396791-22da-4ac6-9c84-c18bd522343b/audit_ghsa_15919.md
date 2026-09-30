# [C] VM images built with Image Builder and Proxmox provider use default credentials in github.com/kubernetes-sigs/image-builder

## Summary
Severity: Critical
Advisory: GHSA-9224-ggvw-wh7v
CVE: CVE-2024-9486
CWE: CWE-798
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-15
Source: https://github.com/advisories/GHSA-9224-ggvw-wh7v
Type: github-advisory

## Affected
- Go: `github.com/kubernetes-sigs/image-builder` — affected >=0 <0.1.38

## Details
A security issue was discovered in the Kubernetes Image Builder versions <= v0.1.37 where default credentials are enabled during the image build process. Virtual machine images built using the Proxmox provider do not disable these default credentials, and nodes using the resulting images may be accessible via these default credentials. The credentials can be used to gain root access. Kubernetes clusters are only affected if their nodes use VM images created via the Image Builder project with its Proxmox provider.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9486
- https://github.com/kubernetes/kubernetes/issues/128006
- https://github.com/kubernetes-sigs/image-builder/pull/1595
- https://github.com/kubernetes-sigs/image-builder
- https://groups.google.com/g/kubernetes-security-announce/c/UKJG-oZogfA/m/Lu1hcnHmAQAJ
