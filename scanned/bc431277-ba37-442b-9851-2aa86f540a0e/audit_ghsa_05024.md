# [H] OpenAM Authenticated RCE via Groovy Sandbox Escape

## Summary
Severity: High
Advisory: GHSA-69j4-qvqr-hpw3
CVE: CVE-2026-47424
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-29
Source: https://github.com/advisories/GHSA-69j4-qvqr-hpw3
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-scripting` — affected >=0 <16.1.1

## Details
## Summary

**Description**

A Protection Mechanism Failure (CWE-693) in OpenAM's server-side scripting sandbox allows an authenticated script author execute operating-system commands from the OpenAM JVM with the default class allow and deny lists. This impacts OpenAM Community Edition through version 16.0.6. This issue was patched in version 16.1.1.

## Impact
An authenticated user (for example, a realm admin) who can create or edit server-side scripts for an executed context can run OS commands as the OpenAM application server admin. For a sub-realm `RealmAdmin`, this crosses the documented boundary from realm-scoped administration to JVM/host execution, effectively compromising the whole OpenAM process and every realm it serves. The sandbox is the only code-level defense between a realm script author and arbitrary JVM/OS execution.

## Patch
This has been patched in OpenAM Community Edition version 16.1.1. Users are encouraged to update to the latest release.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-69j4-qvqr-hpw3
- https://github.com/OpenIdentityPlatform/OpenAM
