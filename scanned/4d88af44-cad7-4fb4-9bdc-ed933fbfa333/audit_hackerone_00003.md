# [H] Windows installer grants low-privileged users write access to executable P2Pool directory, enabling local code execution

## Summary
Severity: High (CVSS 7.3)
Program: Monero
Weakness: Improper Access Control - Generic
Reporter: qttps
State: resolved
Disclosed: 2026-08-20T23:47:52.964Z
Source: https://hackerone.com/reports/3619409

## Details
## Summary

The Windows installer creates the P2Pool subdirectory inside the machine-wide install path with overly broad write permissions:

- `installers/windows/Monero.iss:59`
- `Name: "{app}\p2pool"; Permissions: users-full`

The GUI later trusts and executes `p2pool.exe` from that directory when the user starts P2Pool mining:

- `src/p2pool/P2PoolManager.cpp:124-129` (`isInstalled()` only checks file existence)
- `src/p2pool/P2PoolManager.cpp:154-210` (`start()` executes `p2pool.exe`)
- `src/p2pool/P2PoolManager.cpp:243-248` (Windows path is `{applicationDirPath()}/p2pool/p2pool.exe`)
- `pages/Mining.qml:295-318` and `pages/Mining.qml:654-656` (GUI path to starting P2Pool)

This creates a local binary planting issue: a low-privileged local user can replace or plant `p2pool.exe` in the writable P2Pool directory, and Monero GUI will later execute that attacker-controlled binary when a victim starts P2Pool from the GUI.

## Releases Affected

- Windows installer builds that include commit `432650008c4af92db138041d15b06e43fba0b7ab` dated **2022-05-28** (`Use "p2pool" folder for p2pool on Windows`)
- I have not yet confirmed the earliest tagged release containing this change
- I reviewed the local source tree on **2026-03-20**

## Why This Is Security-Relevant

The affected directory is part of a machine-wide installed application under `Program Files`, but the installer intentionally grants broad write access to ordinary users. That turns a trusted executable location into a user-writable code execution surface.

Because the GUI later launches `p2pool.exe` from that location, any low-privileged local attacker can cause attacker-controlled code to run in the context of whichever user later starts P2Pool from Monero GUI.

This is not a remote issue. It is a local privilege/trust-boundary issue.

## Steps To Reproduce

1. Install Monero GUI on Windows using the normal installer.
2. Confirm that the installer created a writable P2Pool directory:
   - Example target path: `%ProgramFiles%\Monero GUI Wallet\p2pool`
   - Collect ACLs with `icacls "%ProgramFiles%\Monero GUI Wallet\p2pool"`
3. From a low-privileged local user account, place a benign proof-of-concept executable at:
   - `%ProgramFiles%\Monero GUI Wallet\p2pool\p2pool.exe`

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3619409_
