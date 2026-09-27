# [H] File Browser: Command Execution not Limited to Scope

## Summary
Severity: High
Advisory: GHSA-hc8f-m8g5-8362
CVE: CVE-2025-52904
CWE: CWE-77
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-30
Source: https://github.com/advisories/GHSA-hc8f-m8g5-8362
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.33.8

## Details
> [!NOTE]
> **This feature has been disabled by default for all installations from v2.33.8 onwards, including for existent installations**. To exploit this vulnerability, the instance administrator must turn on a feature and ignore all the warnings about known vulnerabilities. We're publishing this new advisory to make it clear that all vulnerabilities concerning this feature are disclosed.
>
> For more information about tracking vulnerability issues related to the Command Execution features, check https://github.com/filebrowser/filebrowser/issues/5199.

## Summary ##

In the web application, all users have a *scope* assigned, and they only have access to the files within that *scope*.
The *Command Execution* feature of Filebrowser allows the execution of shell commands which are not restricted to the scope, potentially giving an attacker read and write access to all files managed by the server.

## Impact ##

Shell commands are executed with the *uid* of the server process without any further restrictions.
This means, that they will have access to at least

* all files managed by the application from all *scopes*, even those the user does not have access to in the GUI.
* the Filebrowser database file containing the password hashes of all accounts.

The concrete impact depends on the commands being granted to the attacker, but due to other vulnerabilities identified ("Bypass Command Execution Allowlist", "Shell Commands Can Spawn Other Commands", "Insecure File Permissions") it is likely, that full read- and write-access will exist.

Read access to the database means, that the attacker is capable of extracting all user password hashes.
This enables an offline dictionary attack on the passwords of all accounts, though the choice of the password hash function (*bcrypt* with a complexity of 10) gives a strong protection against such attacks.
Write access to the database means that attackers are capable of changing a user's password hash, allowing them to impersonate any user account, including an administrator.

## Vulnerability Description ##

Shell commands executed by a user are created as a simple subprocess of the application without any further restrictions.
That means, that they have full access to files accessible by the application.
The *scope* that is assigned to every account is not considered.

As a prerequisite, an attacker needs an account with the `Execute Commands` permission and some permitted commands.

## Proof of Concept ##

Any exploit highly depends on the commands granted to the attacker.
The following screenshot shows, how all password hashes can be extracted using only the `grep` command:

![image](https://github.com/user-attachments/assets/a6fb98e0-2daa-4e10-8480-7963b3d9b214)

## Recommended Countermeasures ##

Until this issue is fixed, we recommend to completely disable `Execute commands` for all accounts.
Since the command execution is an inherently dangerous feature that is not used by all deployments, it should be possible to completely disable it in the application's configuration.
As a defense-in-depth measure, organizations not requiring command execution should operate the Filebrowser from a *distroless* container image.

There are two approaches to fixing this issue:

1. Limiting the process when it is started e.g., by using *user namespaces* with a tool like *Bubblewrap*. If this path is chosen, it is important to use a method that works both on a bare-metal server and within an unprivileged container.
2. Re-architecting the command execution feature so that file in the various *scopes* have a distinct *uid* as an owner and all shell command are executed under the *uid* of the user's *scope*.

## Timeline ##

* `2025-03-26` Identified the vulnerability in version 2.32.0
* `2025-04-11` Contacted the project
* `2025-04-18` Vulnerability disclosed to the project
* `2025-06-25` Uploaded advisories to the project's GitHub repository
* `2025-06-25` CVE ID assigned by GitHub
* `2025-06-25` A patch version has been pushed to disable the feature for all existent installations, and making it **opt-in**. A warning has been added to the documentation and is printed on the console if the feature is enabled. Due to the project being in maintenance-only mode, the bug has not been fixed. Fix is tracked on https://github.com/filebrowser/filebrowser/issues/5199.

## References ##

* [Sandboxing Applications with Bubblewrap: Securing a Basic Shell](https://sloonz.github.io/posts/sandboxing-1/)
* ["Distroless" Container Images.](https://github.com/GoogleContainerTools/distroless)
* [Original Advisory](https://github.com/sbaresearch/advisories/tree/public/2025/SBA-ADV-20250326-01_Filebrowser_Command_Execution_Not_Limited_To_Scope)

## Credits ##

* Mathias Tausig ([SBA Research](https://www.sba-research.org/))

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-hc8f-m8g5-8362
- https://nvd.nist.gov/vuln/detail/CVE-2025-52904
- https://github.com/filebrowser/filebrowser/issues/5199
- https://github.com/GoogleContainerTools/distroless
- https://github.com/filebrowser/filebrowser
- https://github.com/sbaresearch/advisories/tree/public/2025/SBA-ADV-20250326-01_Filebrowser_Command_Execution_Not_Limited_To_Scope
- https://pkg.go.dev/vuln/GO-2025-3793
- https://sloonz.github.io/posts/sandboxing-1
