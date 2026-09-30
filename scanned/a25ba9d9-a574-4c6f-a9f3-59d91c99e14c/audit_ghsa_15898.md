# [M] Vulnerable juju hook tool abstract UNIX domain socket

## Summary
Severity: Medium
Advisory: GHSA-8v4w-f4r9-7h6x
CVE: CVE-2024-8037
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2024-10-03
Source: https://github.com/advisories/GHSA-8v4w-f4r9-7h6x
Type: github-advisory

## Affected
- Go: `github.com/juju/juju` — affected >=0 <0.0.0-20240820065804-2f2ec128ef5a

## Details
### Impact
When combined with an attack of `JUJU_CONTEXT_ID`, any user on the local system with access to the default network namespace may connect to the `@/var/lib/juju/agents/unit-xxxx-yyyy/agent.socket` and perform actions that are normally reserved to a juju charm.

### Patches
Patch: https://github.com/juju/juju/commit/2f2ec128ef5a8ca81fc86ae79cfcdbab0007c206
Patched in:
- 3.5.4
- 3.4.6
- 3.3.7
- 3.1.10
- 2.9.51

### Workarounds
No workarounds available.

### References
[GHSA-mh98-763h-m9v4](https://github.com/juju/juju/security/advisories/GHSA-mh98-763h-m9v4)
https://github.com/juju/juju/blob/725800953aaa29dbeda4f806097bf838e61644dd/worker/uniter/paths.go#L222

## References
- https://github.com/juju/juju/security/advisories/GHSA-8v4w-f4r9-7h6x
- https://github.com/juju/juju/security/advisories/GHSA-mh98-763h-m9v4
- https://nvd.nist.gov/vuln/detail/CVE-2024-8037
- https://github.com/juju/juju/commit/2f2ec128ef5a8ca81fc86ae79cfcdbab0007c206
- https://github.com/juju/juju
- https://github.com/juju/juju/blob/725800953aaa29dbeda4f806097bf838e61644dd/worker/uniter/paths.go#L222
- https://pkg.go.dev/vuln/GO-2024-3174
