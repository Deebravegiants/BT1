# [C] Spinnaker: RCE via expression parsing due to unrestricted context handling

## Summary
Severity: Critical
Advisory: GHSA-69rw-45wj-g4v6
CVE: CVE-2026-32613
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-69rw-45wj-g4v6
Type: github-advisory

## Affected
- Maven: `io.spinnaker.echo:echo-pipelinetriggers` — affected >=2026.0-0 <2026.0.1
- Maven: `io.spinnaker.echo:echo-pipelinetriggers` — affected >=2025.4-0 <2025.4.2
- Maven: `io.spinnaker.echo:echo-pipelinetriggers` — affected >=0 <2025.3.2

## Details
Spinnaker is an open source, multi-cloud continuous delivery platform. Echo like some other services, uses SPeL (Spring Expression Language) to process information - specifically around expected artifacts. In versions prior to 2026.1.0, 2026.0.1, 2025.4.2, and 2025.3.2, unlike orca, it was NOT restricting that context to a set of trusted classes, but allowing FULL JVM access. This enabled a user to use arbitrary java classes which allow deep access to the system. This enabled the ability to invoke commands, access files, etc. Versions 2026.1.0, 2026.0.1, 2025.4.2, and 2025.3.2 contain a patch. As a workaround, disable echo entirely.

## References
- https://github.com/spinnaker/spinnaker/security/advisories/GHSA-69rw-45wj-g4v6
- https://nvd.nist.gov/vuln/detail/CVE-2026-32613
- https://github.com/spinnaker/spinnaker
- https://github.com/spinnaker/spinnaker/releases/tag/spinnaker-release-2025.3.2
- https://github.com/spinnaker/spinnaker/releases/tag/spinnaker-release-2025.4.2
- https://github.com/spinnaker/spinnaker/releases/tag/spinnaker-release-2026.0.1
- https://github.com/spinnaker/spinnaker/releases/tag/spinnaker-release-2026.0.2
- https://zeropath.com/blog/spinnaker-rce-production-compromise
