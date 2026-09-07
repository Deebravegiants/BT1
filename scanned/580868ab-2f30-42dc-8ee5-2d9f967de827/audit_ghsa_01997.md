# [M] Permissions bypass in KubeVirt

## Summary
Severity: Medium
Advisory: GHSA-849r-8wvp-4wwg
CVE: CVE-2020-1701
CWE: CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-06-01
Source: https://github.com/advisories/GHSA-849r-8wvp-4wwg
Type: github-advisory

## Affected
- Go: `kubevirt.io/kubevirt` — affected >=0 <0.26.0

## Details
A flaw was found in the KubeVirt main virt-handler versions before 0.26.0 regarding the access permissions of virt-handler. An attacker with access to create VMs could attach any secret within their namespace, allowing them to read the contents of that secret.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1701
- https://github.com/kubevirt/kubevirt/issues/2967
- https://github.com/kubevirt/containerized-data-importer/pull/1098
- https://github.com/kubevirt/kubevirt/pull/3001
- https://github.com/kubevirt/kubevirt/commit/9efa8d7388d4fe1c698c6980aa7122c06bd141be
- https://bugzilla.redhat.com/show_bug.cgi?id=1792092
- https://github.com/kubevirt/kubevirt
