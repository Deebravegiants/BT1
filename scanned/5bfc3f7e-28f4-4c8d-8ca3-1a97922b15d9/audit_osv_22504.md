# [H] Improper Access Control in kctf

## Summary
Severity: High
Advisory: CVE-2022-31055
Aliases: GHSA-4g2v-6qc6-6jv5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-06-13
Source: https://osv.dev/vulnerability/CVE-2022-31055
Type: osv

## Details
kCTF is a Kubernetes-based infrastructure for capture the flag (CTF) competitions. Prior to version 1.6.0, the kctf cluster set-src-ip-ranges was broken and allowed traffic from any IP. The problem has been patched in v1.6.0. As a workaround, those who want to test challenges privately can mark them as `public: false` and use `kctf chal debug port-forward` to connect.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31055.json
- https://github.com/google/kctf/security/advisories/GHSA-4g2v-6qc6-6jv5
- https://nvd.nist.gov/vuln/detail/CVE-2022-31055
- https://github.com/google/kctf/commit/8cf050be974fcc2fd8aa136701f9a66f2b2a5202
- https://github.com/google/kctf/pull/371
