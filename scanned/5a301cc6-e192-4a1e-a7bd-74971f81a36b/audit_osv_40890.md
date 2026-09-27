# [C] obs-service-tar_scm: command injection via mercurial handler

## Summary
Severity: Critical
Advisory: CVE-2026-56004
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-56004
Type: osv

## Details
A shellcode injection in the mercurial handler of the obs tar_scm source service before version 0.12.4 could be used by attackers able to provide a _service file to execute code as the source service or the local user checking out the malicious services

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56004.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56004
- https://github.com/openSUSE/obs-service-tar_scm/pull/552/changes/bcf29d318c671c45fe87dd9f995a4a0c78ecedd7
- https://github.com/openSUSE/obs-service-tar_scm
