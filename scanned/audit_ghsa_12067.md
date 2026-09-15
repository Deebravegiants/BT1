# [C] OpenSTAManager affected by unauthenticated privilege escalation via modules/utenti/actions.php

## Summary
Severity: Critical
Advisory: GHSA-247v-7cw6-q57v
CVE: CVE-2026-27012
CWE: CWE-306
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-247v-7cw6-q57v
Type: github-advisory

## Affected
- Packagist: `devcode-it/openstamanager` — affected >=0

## Details
### Summary
A privilege escalation and authentication bypass vulnerability in OpenSTAManager allows any attacker to arbitrarily change a user's group (`idgruppo`) by directly calling `modules/utenti/actions.php`. This can promote an existing account (e.g. agent) into the Amministratori group as well as demote any user including existing administrators.

### Details
`modules/utenti/actions.php` is reachable directly via `http://<IP>:8080/modules/utenti/actions.php` and processes privileged information without requiring any authentication or authorization checks on fields like idgruppo. As a result, an attacker can submit a crafted POST request that updates the targets record and assigns it to the administrator group.

The file explicitly sets:
```PHP
$skip_permissions = true;
include_once __DIR__.'/../../core.php';
```
`core.php` then invokes:

```PHP
Permissions::skip();
```
Thus, disabling any authentication and permission enforcement. As a result, this file processes operations based on the `op` parameter in the POST request, not only `update_user`. Sensitive fields like `idgruppo` and others can be updated without verifying anything.

### PoC
A target username exists, such as "agent" with an ID of 4. No authentication or cookies are required. Send the following POST request via Burp Suite or similar:
<img width="1094" height="255" alt="image" src="https://github.com/user-attachments/assets/2e8cb148-1b5d-4e5c-9c73-05ed75d64188" />
The target's group is updated in the database.
Verify the changes in the database before and after the POST request:
<img width="1053" height="430" alt="image" src="https://github.com/user-attachments/assets/49f63ca0-8a04-4dd1-b27c-69699d2ce26f" />
Changes also visible in the administrator panel, they have been moved from the Agenti group to Amministratori.

### Impact
An unauthenticated attacker can assign administrator privileges to existing users, modify group memberships, enable/disable accounts and other operations that are exposed in the file. This can lead to a full compromise of the application.

## References
- https://github.com/devcode-it/openstamanager/security/advisories/GHSA-247v-7cw6-q57v
- https://github.com/devcode-it/openstamanager
