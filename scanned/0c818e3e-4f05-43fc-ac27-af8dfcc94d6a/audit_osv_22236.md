# [H] CVE-2022-23948

## Summary
Severity: High
Advisory: CVE-2022-23948
Aliases: GHSA-wj36-qcfg-5j52
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-21
Source: https://osv.dev/vulnerability/CVE-2022-23948
Type: osv

## Details
A flaw was found in Keylime before 6.3.0. The logic in the Keylime agent for checking for a secure mount can be fooled by previously created unprivileged mounts allowing secrets to be leaked to other processes on the host.

## References
- https://seclists.org/oss-sec/2022/q1/101
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23948.json
- https://github.com/keylime/keylime/security/advisories/GHSA-wj36-qcfg-5j52
- https://nvd.nist.gov/vuln/detail/CVE-2022-23948
- https://github.com/keylime/keylime/commit/1a4f31a6368d651222683c9debe7d6832db6f607
- https://github.com/keylime/keylime/commit/d37c406e69cb6689baa2fb7964bad75209703724
