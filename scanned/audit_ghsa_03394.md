# [M] Exposure of Resource to Wrong Sphere and Insecure Temporary File in Ansible

## Summary
Severity: Medium
Advisory: GHSA-77g3-3j5w-64w4
CVE: CVE-2020-10685
CWE: CWE-377, CWE-459, CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-04-07
Source: https://github.com/advisories/GHSA-77g3-3j5w-64w4
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.7.0a1 <2.7.17
- PyPI: `ansible` — affected >=2.8.0a1 <2.8.11
- PyPI: `ansible` — affected >=2.9.0a1 <2.9.7

## Details
A flaw was found in Ansible Engine affecting Ansible Engine versions 2.7.x before 2.7.17 and 2.8.x before 2.8.11 and 2.9.x before 2.9.7 as well as Ansible Tower before and including versions 3.4.5 and 3.5.5 and 3.6.3 when using modules which decrypts vault files such as assemble, script, unarchive, win_copy, aws_s3 or copy modules. The temporary directory is created in /tmp leaves the s ts unencrypted. On Operating Systems which /tmp is not a tmpfs but part of the root partition, the directory is only cleared on boot and the decryp emains when the host is switched off. The system will be vulnerable when the system is not running. So decrypted data must be cleared as soon as possible and the data which normally is encrypted ble.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10685
- https://github.com/ansible/ansible/pull/68433
- https://github.com/ansible/ansible/commit/4e1fe80e681fa466626e9dea53efe6b0253ea1b2
- https://github.com/ansible/ansible/commit/51d2514753544a9d58cd7524e27e696b2c944fb5
- https://github.com/ansible/ansible/commit/e1273b6faf036ed84e4f4edee85b888a4e256aee
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10685
- https://github.com/advisories/GHSA-77g3-3j5w-64w4
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2020-1.yaml
- https://security.gentoo.org/glsa/202006-11
- https://www.debian.org/security/2021/dsa-4950
