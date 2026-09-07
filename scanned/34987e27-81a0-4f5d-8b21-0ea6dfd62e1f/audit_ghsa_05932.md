# [H] LibreNMS Vulnerable to Remote Code Execution by Signal Alert Transportation module

## Summary
Severity: High
Advisory: GHSA-c9fv-cgmm-2wg7
CVE: CVE-2026-55182
CWE: CWE-77
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-c9fv-cgmm-2wg7
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=21.6.0 <26.5.0

## Details
### Summary
A vulnerability has been identified that allows an authenticated administrator to execute arbitrary code on the host server. By adding an alert transport entry, an attacker with administrative privileges can execute malicious commands.

### Details
The vulnerability is caused by an unsafe `exec` call in `deliverAlert` function of `LibreNMS/Alert/Transport/Signal.php`. Escapes for the path of `signal-cli` and the `Recipient` field are insufficient to prevent command-line injection. 

The `composer_wrapper.php` under `scripts` is also vulnerable to command injection (unsafe `exec` calls) by passing the injected command as an argument, and it is accepting arguments passed by `deliverAlert`.

By chaining these unsafe `exec` calls, malicious admin user can execute any executables in the server's filesystem.

### PoC

1. Under Dashboard -> Alert -> Alert Transports

<img width="282" height="273" alt="image" src="https://github.com/user-attachments/assets/b72f55b0-b782-47d0-b4f7-75f498019345" />

2. Create a new Alert Transport entry.
    a. Select `Signal` as `Transport type`.
    b. Put `../scripts/composer_wrapper.php` into `Path`.
    c. Put the command to execute under `Recipient` with `;` at the start and the end of string.

<img width="767" height="391" alt="image" src="https://github.com/user-attachments/assets/5e34bfa8-4bd5-40cb-9624-0d40e40ccdc5" />

3. . Click `Save Transport`, and after the popup closed, click `Test Transport` button under `Action` of the created Alert Transport entry.

<img width="172" height="90" alt="image" src="https://github.com/user-attachments/assets/7f83db07-fbf9-4be6-b247-533a6d7b9828" />

4. The command is executed.
<img width="532" height="216" alt="image" src="https://github.com/user-attachments/assets/d595b0fe-10cc-4050-b4b9-d290b658689d" />

### Impact
This vulnerability allows a malicious actor to achieve Remote Code Execution (RCE), potentially leading to complete system compromise, data exfiltration, or lateral movement within the network.

### Remediation Advice
Escape user inputs, and avoid passing them directly into `exec` function. (`scripts/composer_wrapper.php`)
Avoid setting executable paths directly in web interface. Instead, use a config value, and only allow setting executable paths by command line interface. (`LibreNMS/Alert/Transport/Signal.php`)

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-c9fv-cgmm-2wg7
- https://github.com/librenms/librenms
- https://github.com/librenms/librenms/releases/tag/26.5.0
