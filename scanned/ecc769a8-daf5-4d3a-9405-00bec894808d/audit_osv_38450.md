# [H] Zarf has a Path Traversal via Malicious Package Metadata.Name — Arbitrary File Write

## Summary
Severity: High
Advisory: CVE-2026-40090
Aliases: GHSA-pj97-4p9w-gx3q, GO-2026-5542
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:L)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-40090
Type: osv

## Details
Zarf is an Airgap Native Packager Manager for Kubernetes. Versions 0.23.0 through 0.74.1 contain an arbitrary file write vulnerability in the zarf package inspect sbom and zarf package inspect documentation subcommands. These subcommands output file paths are constructed by joining a user-controlled output directory with the package's Metadata.Name field read directly from the untrusted package's zarf.yaml manifest. Although Metadata.Name is validated against a regex on package creation, an attacker can unarchive a package to modify the Metadata.Name field to contain path traversal sequences such as ../../etc/cron.d/malicious or absolute paths like /home/user/.ssh/authorized_keys, along with the corresponding files inside SBOMS.tar. This allows writing attacker-controlled content to arbitrary filesystem locations within the permissions of the user running the inspect command. This issue has been fixed in version 0.74.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40090.json
- https://github.com/zarf-dev/zarf/security/advisories/GHSA-pj97-4p9w-gx3q
- https://nvd.nist.gov/vuln/detail/CVE-2026-40090
- https://github.com/zarf-dev/zarf/pull/4793
