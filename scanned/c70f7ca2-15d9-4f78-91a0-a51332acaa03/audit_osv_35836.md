# [H] Argo-cd: argo cd unauthenticated remote code execution in repo-server via generatemanifest grpc endpoint

## Summary
Severity: High
Advisory: CVE-2026-15416
Aliases: CVE-2026-62185, GHSA-47m3-95c7-g2g8
CVSS: 8.9 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-15416
Type: osv

## Details
A flaw was identified in Argo CD, the GitOps engine used by Red Hat OpenShift GitOps, that could allow an unauthenticated attacker with network access to the Argo CD repo-server to achieve remote code execution. Under certain conditions, the attacker may then manipulate cached data to deploy malicious Kubernetes resources to managed clusters, potentially resulting in complete cluster compromise.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://thehackernews.com/2026/07/unpatched-argo-cd-repo-server-flaw.html
- https://www.synacktiv.com/en/publications/caught-in-the-octopus-trap-unauthenticated-rce-in-argo-cd-with-codeql
- https://access.redhat.com/errata/RHSA-2026:52857
- https://access.redhat.com/security/cve/CVE-2026-15416
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15416.json
- https://github.com/argoproj/argo-helm/security/advisories/GHSA-47m3-95c7-g2g8
- https://nvd.nist.gov/vuln/detail/CVE-2026-15416
- https://bugzilla.redhat.com/show_bug.cgi?id=2496732
- https://github.com/argoproj/argo-helm/commit/0f245ab
- https://github.com/argoproj/argo-helm
