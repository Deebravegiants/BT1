# [H] Kubeflow Community Distribution: Overly Permissive Istio Permissions Allows Kubeflow Authorization Token Stealing

## Summary
Severity: High
Advisory: CVE-2026-47237
Aliases: GHSA-v824-8gxh-pgjw
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-47237
Type: osv

## Details
Kubeflow Community Distribution helps users to install Kubeflow Platform in popular Kubernetes clusters. Prior to version 26.03-rc.1, a Kubeflow setup based on the official manifests or most other packaged Kubeflow distributions is vulnerable to authorization token stealing from any user of the Kubeflow UI or APIs, such as the Dashboard, Pipelines API, or Notebooks. With this token, the attacker can take over the user's account and the data that is processed by that user. The attacker needs a valid user with the ``kubeflow-edit`` role / Contributor role in a random Kubeflow namespace to perform this attack. This is given if _Automatic Profile Creation_ is enabled. Version 26.03-rc.1 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47237.json
- https://github.com/kubeflow/community-distribution/security/advisories/GHSA-v824-8gxh-pgjw
- https://nvd.nist.gov/vuln/detail/CVE-2026-47237
- https://github.com/kubeflow/community-distribution/commit/31b2411dda319bfeae8686ecdf3a39436ec32ce2
- https://github.com/kubeflow/community-distribution/pull/3043
