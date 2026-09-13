# [H] Yggdrasil-worker-package-manager: yggdrasil-worker-package-manager: remote code execution via apt argument injection

## Summary
Severity: High
Advisory: CVE-2026-18157
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-18157
Type: osv

## Details
A flaw was found in yggdrasil-worker-package-manager. A local attacker with existing access to the system could exploit an argument injection vulnerability in the APT backend. This allows specially crafted package names, which begin with a hyphen, to be misinterpreted as command options by apt-get. Successful exploitation could lead to remote code execution (RCE) with root privileges, enabling the attacker to fully compromise the system's integrity, confidentiality, and availability.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://github.com/RedHatInsights/yggdrasil-worker-package-manager/releases/tag/0.1.4
- https://github.com/RedHatInsights/yggdrasil-worker-package-manager/releases/tag/0.2.4
- https://access.redhat.com/security/cve/CVE-2026-18157
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18157.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18157
- https://bugzilla.redhat.com/show_bug.cgi?id=2465250
- https://github.com/RedHatInsights/yggdrasil-worker-package-manager/commit/959745bb5917c17f0316af199aace6c71baa5ad7
- https://github.com/RedHatInsights/yggdrasil-worker-package-manager
