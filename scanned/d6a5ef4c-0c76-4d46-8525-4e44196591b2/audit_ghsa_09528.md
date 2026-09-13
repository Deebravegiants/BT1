# [M] Sparkle's AppInstaller post-stage-1 XPC listener accepts unvalidated connections, allowing spoofed appcast item data injection

## Summary
Severity: Medium
Advisory: GHSA-g3hp-f6mg-559v
CVE: CVE-2026-47122
CWE: CWE-306, CWE-441
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-g3hp-f6mg-559v
Type: github-advisory

## Affected
- SwiftURL: `github.com/sparkle-project/Sparkle` — affected >=0

## Details
## Summary

AppInstaller post-stage-1 XPC listener accepts unvalidated connections, allowing spoofed appcast item data injection.

## Details

`Autoupdate/AppInstaller.m`'s `shouldAcceptNewConnection:` only enforces `SUCodeSigningVerifier validateConnection:` before stage 1 completes. After `_performedStage1Installation = YES`, new connections to the registered Mach service `<bundleId>-spki` are accepted from any local process without team-ID or code-signing checks.

The following chain of events enables an attacker to inject a spoofed `SPUSentUpdateAppcastItemData` payload:

1. Installer finishes unarchiving the update successfully (`_willCompleteInstallation` is set).
2. The app responsible for updating the bundle crashes or is forcefully quit before it has a chance to send `SPUSentUpdateAppcastItemData` to the installer. There is no user interaction between the prior step and this one, so the timing window is tight.
3. After stage 1 of the installer is performed (`_performedStage1Installation = YES`), but before final installation completes (since all services are cleaned up by then), an attacker process connects to the `<bundleId>-spki` Mach service - no code-signing validation is enforced - and sends a spoofed `SPUSentUpdateAppcastItemData` message containing an attacker-crafted `SUAppcastItem`.
4. A Sparkle-aware app that checks for updates on the bundle being updated launches before installation completes. The progress agent re-broadcasts the spoofed `SUAppcastItem` on its `<bundleId>-spks` status service, and the launching app displays attacker-controlled release notes (name, version, critical flag).

Note: Sparkle can be used to update other app bundles, so the "app doing the updating" and the "app being updated" are not necessarily the same bundle.

In the system-domain case (`SPUUsesSystemDomainForBundlePath = true`), the AppInstaller runs as root via `SMJobSubmit` to `kSMDomainSystemLaunchd`, and the Mach service is reachable by any local user process.

Affected versions: 2.x branch including 2.9.1.

## Impact

A local user-level process can inject a forged `SUAppcastItem` (arbitrary name, version, critical flag) into the progress agent's status broadcast. Other Sparkle-aware clients on the system will display attacker-controlled release notes as authoritative installation state.

The integrity of the installed code is **not** affected - the bundle moved into place is the legitimate, signature-validated update from stage 1. The impact is limited to UI spoofing of installation metadata.

## Remediation

Enforce `SUCodeSigningVerifier validateConnection:` on all new connections regardless of installation stage, or disallow `SPUSentUpdateAppcastItemData` after the active connection invalidates.

## References
- https://github.com/sparkle-project/Sparkle/security/advisories/GHSA-g3hp-f6mg-559v
- https://github.com/sparkle-project/Sparkle
