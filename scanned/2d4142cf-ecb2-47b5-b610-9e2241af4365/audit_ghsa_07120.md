# [H] Trivy: Helm chart tar bomb causes OOM via unbounded io.ReadAll in parser

## Summary
Severity: High
Advisory: GHSA-q3fv-x8vg-qqm4
CVE: CVE-2026-54448
CWE: CWE-400, CWE-770, CWE-789
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-q3fv-x8vg-qqm4
Type: github-advisory

## Affected
- Go: `github.com/aquasecurity/trivy` — affected >=0 <0.71.0

## Details
## Summary

When Trivy scans a Helm chart archive (`.tgz`), its custom tar unpacker reads each entry with `io.ReadAll(tr)` and no size limit. An attacker who can place a malicious `.tgz` file in the scanned path can craft a small compressed archive that decompresses to gigabytes, causing the Trivy process to be killed by the OS OOM killer.

## Affected configurations

Exploitation requires the attacker to place a crafted `.tgz` file in a location that Trivy will scan as a Helm chart. This applies to the following scan targets:

| Command | Condition |
| --- | --- |
| `trivy config <dir>` | Directory contains a crafted `.tgz` Helm chart (misconfiguration scanning is always enabled) |
| `trivy filesystem --scanners misconf <dir>` | Directory contains a crafted `.tgz` Helm chart **and** `--scanners misconf` is explicitly enabled |
| `trivy image --scanners misconf <image>` | Image contains a crafted `.tgz` Helm chart **and** `--scanners misconf` is explicitly enabled |

Realistic scenarios include:
- A CI pipeline that runs `trivy config .` on a repository where a contributor can submit a pull request containing a crafted chart archive.
- A pipeline that scans a container image with `--scanners misconf`, whose build context includes untrusted `.tgz` files.

## Impact

An attacker who satisfies the conditions above can exhaust all available memory on the host running Trivy. The OS OOM killer will terminate the Trivy process and may affect other processes sharing the same host or CI runner.

The practical impact in CI environments is denial of service: the scan fails, the pipeline is blocked, and repeated submissions re-trigger the same condition. Cloud CI runners may also incur additional costs for consumed resources.

There is no impact on confidentiality or integrity of the scanned system.

## Patches

Fixed in Trivy `v0.71.0` (#10718). The custom tar unpacker was replaced with `archive.LoadArchiveFiles` from the official `helm.sh/helm/v4` SDK, which enforces per-entry and total size limits and validates archive structure. Users should upgrade to `v0.71.0` or later.

## Workarounds

If upgrading is not immediately possible:
- Set a memory limit (cgroup/container) on the Trivy process to bound the blast radius.
- Use `--skip-dirs` to exclude directories containing untrusted Helm chart archives from the scan.
- Avoid scanning repositories or images with untrusted `.tgz` files.

## Credits

Reported by @jamesgol.

## References
- https://github.com/aquasecurity/trivy/security/advisories/GHSA-q3fv-x8vg-qqm4
- https://nvd.nist.gov/vuln/detail/CVE-2026-54448
- https://github.com/aquasecurity/trivy/pull/10718
- https://github.com/aquasecurity/trivy/commit/441251e51ae46cbcf7f436547e0a5766b25328b4
- https://github.com/aquasecurity/trivy
- https://github.com/aquasecurity/trivy/releases/tag/v0.71.0
