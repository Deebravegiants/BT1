# [M] Openssh: double free in red hat enterprise linux versions of openssh dh-gex client path during fips known-group validation leads to client-side denial of service

## Summary
Severity: Medium
Advisory: CVE-2026-55653
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-55653
Type: osv

## Details
A flaw was found in OpenSSH. A malicious SSH server can exploit a double free vulnerability in the Diffie-Hellman Group Exchange (DH-GEX) client path. This occurs during FIPS (Federal Information Processing Standards) mode known-group validation when the client processes attacker-controlled DH-GEX group parameters. Successful exploitation leads to client-side process termination, resulting in a Denial of Service (DoS).

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:36759
- https://access.redhat.com/errata/RHSA-2026:47755
- https://access.redhat.com/errata/RHSA-2026:47756
- https://access.redhat.com/errata/RHSA-2026:47757
- https://access.redhat.com/errata/RHSA-2026:54387
- https://access.redhat.com/errata/RHSA-2026:58981
- https://access.redhat.com/security/cve/CVE-2026-55653
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55653.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55653
- https://bugzilla.redhat.com/show_bug.cgi?id=2462351
