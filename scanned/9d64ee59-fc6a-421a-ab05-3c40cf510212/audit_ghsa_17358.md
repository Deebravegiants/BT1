# [H] Grav vulnerable to Path traversal / arbitrary YAML write via user creation leading to Account Takeover / System Corruption

## Summary
Severity: High
Advisory: GHSA-h756-wh59-hhjv
CVE: CVE-2025-66295
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-h756-wh59-hhjv
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.8.0-beta.27

## Details
### Summary
When a user with privilege of user creation creates a new user through the Admin UI and supplies a username containing path traversal sequences (for example ..\Nijat or ../Nijat), Grav writes the account YAML file to an unintended path outside user/accounts/. The written YAML can contain account fields such as email, fullname, twofa_secret, and hashed_password. In my tests,  I was able to cause the Admin UI to write the following content into arbitrary .yaml files (including files like email.yaml, system.yaml, or other site YAML files like admin.yaml) — demonstrating arbitrary YAML write / overwrite via the Admin UI.

Example observed content written by the Admin UI (test data):
username: ..\Nijat
state: enabled
email: [EMAIL@gmail.com](mailto:EMAIL@gmail.com)
fullname: 'Nijat Alizada'
language: en
content_editor: default
twofa_enabled: false
twofa_secret: RWVEIHC2AFVD6FCR6UHCO3DS4HWXKKDT
avatar: { }
hashed_password: $2y$10$wl9Ktv3vUmDKCt8o6u2oOuRZr1I04OE0YZf2sJ1QcAherbNnk1XVC
access:
site:
login: true


### Steps to Reproduce
1. Log in to the Grav Admin UI as an administrator.
2. Create a new user with the following values (example):
        a. Username: ..\POC-TOKEN-2025-09-29
        b. Fullname: POC-TOKEN-2025-09-29
        c. Email: poc+2025-09-29@example.test
        d. Password: (any password)
Observe that a YAML file containing the POC-TOKEN is written outside user/accounts/ (for example in the parent directory of user/accounts)


### Impact
1. Config corruption / service disruption: Overwriting system.yaml, email.yaml, or plugin config files with attacker-controlled YAML (even if limited to fields present in account YAML) could break functionality, disable services, or cause misconfiguration requiring recovery from backups.
2. Account takeover, any user with create user privilege can modify other user's email and password by just creating a new user with the name "..\accounts\USERNAME_OF_VICTIM"


### Proof of Concept
https://github.com/user-attachments/assets/cf503d74-f765-4031-8e22-71f6b3630847

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-h756-wh59-hhjv
- https://nvd.nist.gov/vuln/detail/CVE-2025-66295
- https://github.com/getgrav/grav/commit/3462d94d575064601689b236508c316242e15741
- https://github.com/getgrav/grav
