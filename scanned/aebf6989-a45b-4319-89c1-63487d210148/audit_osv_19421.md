# [H] CVE-2021-21261

## Summary
Severity: High
Advisory: CVE-2021-21261
Aliases: GHSA-4ppf-fxf6-vxg2
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-01-14
Source: https://osv.dev/vulnerability/CVE-2021-21261
Type: osv

## Details
Flatpak is a system for building, distributing, and running sandboxed desktop applications on Linux. A bug was discovered in the `flatpak-portal` service that can allow sandboxed applications to execute arbitrary code on the host system (a sandbox escape). This sandbox-escape bug is present in versions from 0.11.4 and before fixed versions 1.8.5 and 1.10.0. The Flatpak portal D-Bus service (`flatpak-portal`, also known by its D-Bus service name `org.freedesktop.portal.Flatpak`) allows apps in a Flatpak sandbox to launch their own subprocesses in a new sandbox instance, either with the same security settings as the caller or with more restrictive security settings. For example, this is used in Flatpak-packaged web browsers such as Chromium to launch subprocesses that will process untrusted web content, and give those subprocesses a more restrictive sandbox than the browser itself. In vulnerable versions, the Flatpak portal service passes caller-specified environment variables to non-sandboxed processes on the host system, and in particular to the `flatpak run` command that is used to launch the new sandbox instance. A malicious or compromised Flatpak app could set environment variables that are trusted by the `flatpak run` command, and use them to execute arbitrary code that is not in a sandbox. As a workaround, this vulnerability can be mitigated by preventing the `flatpak-portal` service from starting, but that mitigation will prevent many Flatpak apps from working correctly. This is fixed in versions 1.8.5 and 1.10.0.

## References
- https://github.com/flatpak/flatpak/commit/cc1401043c075268ecc652eac557ef8076b5eaba
- https://github.com/flatpak/flatpak/releases/tag/1.8.5
- https://github.com/flatpak/flatpak/security/advisories/GHSA-4ppf-fxf6-vxg2
- https://security.gentoo.org/glsa/202101-21
- https://www.debian.org/security/2021/dsa-4830
- https://github.com/flatpak/flatpak/commit/6d1773d2a54dde9b099043f07a2094a4f1c2f486
- https://github.com/flatpak/flatpak/commit/6e5ae7a109cdfa9735ea7ccbd8cb79f9e8d3ae8b
- https://github.com/flatpak/flatpak/commit/aeb6a7ab0abaac4a8f4ad98b3df476d9de6b8bd4
