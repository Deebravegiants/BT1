# [M] VM images built with Image Builder with some providers use default credentials during builds in github.com/kubernetes-sigs/image-builder

## Summary
Severity: Medium
Advisory: GHSA-8jpg-62jc-hwhr
CVE: CVE-2024-9594
CWE: CWE-798
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-15
Source: https://github.com/advisories/GHSA-8jpg-62jc-hwhr
Type: github-advisory

## Affected
- Go: `github.com/kubernetes-sigs/image-builder` — affected >=0 <0.1.38

## Details
A security issue was discovered in the Kubernetes Image Builder versions <= v0.1.37 where default credentials are enabled during the image build process when using the Nutanix, OVA, QEMU or raw providers. The credentials can be used to gain root access. The credentials are disabled at the conclusion of the image build process. Kubernetes clusters are only affected if their nodes use VM images created via the Image Builder project. Because these images were vulnerable during the image build process, they are affected only if an attacker was able to reach the VM where the image build was happening and used the vulnerability to modify the image at the time the image build was occurring.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9594
- https://github.com/kubernetes/kubernetes/issues/128007
- https://github.com/kubernetes-sigs/image-builder/pull/1596
- https://groups.google.com/g/kubernetes-security-announce/c/UKJG-oZogfA/m/Lu1hcnHmAQAJ
