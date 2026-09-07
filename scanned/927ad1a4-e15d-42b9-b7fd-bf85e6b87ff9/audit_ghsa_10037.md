# [M] beets has a Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3gxm-wfjx-m847
CVE: CVE-2026-42052
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-3gxm-wfjx-m847
Type: github-advisory

## Affected
- PyPI: `beets` — affected >=0 <2.10.0

## Details
During code logic analyis, an area that may lead to unintended behavior under specific conditions was discovered. 

## Overview
- Verified Version: `80cd21554124da07d17a4f962c7d770a4f70d0f2`
- Vulnerability Type: Stored XSS
- Affected Location: `beetsplug/web/templates/index.html:42`
- Trigger Scenario: Metadata fields such as `title`, `lyrics`, or `comments` are rendered with raw template interpolation and inserted into DOM via `.html(...)`.

## Root Cause
The bundled web UI uses Underscore template interpolation mode `<%= ... %>` for untrusted metadata fields. In this runtime, `<%= ... %>` is raw insertion and HTML escaping is only performed by `<%- ... %>`. Rendered output is then inserted with `.html(...)`, allowing attacker-controlled markup to become active DOM.

## Source-to-Sink Chain
1. Source (attacker-controlled input)
- Item metadata values (for example `title`, `lyrics`, `comments`) can contain attacker HTML payload.

2. Data flow
- Templates in `beetsplug/web/templates/index.html:42-46,87-91` render metadata with `<%= ... %>`.
- Underscore runtime defines `<%= ... %>` as raw interpolation (`beetsplug/web/static/underscore.js:890-907`).

3. Sink (security-sensitive action)
- Frontend inserts rendered template output into DOM via `$(this.el).html(this.template(this.model.toJSON()));` in `beetsplug/web/static/beets.js:182,208,220`.

## Exploitation Preconditions
1. Victim opens the web UI page that renders attacker-controlled metadata.
2. Metadata includes executable HTML/JS payload.

## Risk
Stored payload executes in the web UI context and can perform actions available to that origin.

## Impact
Attacker can run arbitrary JavaScript in the victim browser, exfiltrate viewable data, and perform UI-driven actions as the victim session.

## Remediation
1. Replace raw interpolation `<%= ... %>` with escaped output `<%- ... %>` for untrusted fields.
2. Avoid `.html(...)` for untrusted template output; use text-safe rendering.
3. Sanitize metadata values on ingest and before rendering, including attribute contexts.

## References
- https://github.com/beetbox/beets/security/advisories/GHSA-3gxm-wfjx-m847
- https://nvd.nist.gov/vuln/detail/CVE-2026-42052
- https://github.com/beetbox/beets
- https://github.com/beetbox/beets/releases/tag/v2.10.0
- https://lists.debian.org/debian-lts-announce/2026/06/msg00030.html
