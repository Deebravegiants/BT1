# [H] Skupper: skupper-cli: flawed authentication method may lead to arbitrary file read or denial of service

## Summary
Severity: High
Advisory: CVE-2024-12582
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2024-12-24
Source: https://osv.dev/vulnerability/CVE-2024-12582
Type: osv

## Details
A flaw was found in the skupper console,  a read-only interface that renders cluster network, traffic details, and metrics for a network application that a user sets up across a hybrid multi-cloud environment. When the default authentication method is used, a random password is generated for the "admin" user and is persisted in either a Kubernetes secret or a podman volume in a plaintext file. This authentication method can be manipulated by an attacker, leading to the reading of any user-readable file in the container filesystem, directly impacting data confidentiality. Additionally, the attacker may induce skupper to read extremely large files into memory, resulting in resource exhaustion and a denial of service attack.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://github.com/skupperproject/skupper/
- https://access.redhat.com/errata/RHSA-2025:1413
- https://access.redhat.com/security/cve/CVE-2024-12582
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12582.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12582
- https://bugzilla.redhat.com/show_bug.cgi?id=2333540
- https://github.com/skupperproject/skupper/pull/1833
