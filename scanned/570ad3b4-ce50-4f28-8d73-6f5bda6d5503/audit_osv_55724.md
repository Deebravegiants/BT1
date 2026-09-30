# [M] gix-sec safe.directory protections absent for elevated administrators

## Summary
Severity: Medium
Advisory: GHSA-7rhf-42qf-vrvc
Aliases: CVE-2025-24890
Ecosystem: crates.io
Published: 2026-09-09
Source: https://osv.dev/vulnerability/GHSA-7rhf-42qf-vrvc
Type: osv

## Affected
- crates.io: `gix-sec` — affected >=0 <0.13.3

## Details
### Summary

In a process run with full administrative rights on Windows, `gix-sec` wrongly treats all locations as trusted, leading to the execution of commands configured in repositories controlled by limited user accounts.

### Details

In a similar way to Git, gitoxide tries to avoid operating in local repositories that it neither considers to be owned by the current user nor finds to match any value of `safe.directory`. [This is because](https://git-scm.com/docs/git.html#_security) of the numerous commands that can be configured for a Git repository, to run as part of various actions, some of which even occur automatically due to the way custom shell prompts and text editors update their knowledge of repositories.

On Unix-like operating systems, every directory is considered to be owned by some user ID. On Windows, other identities can own a directory in the same sense that a user can, and directories created while operating with full administrative rights default to being owned by the `Administrators` group, not the specific user. Such administrators should be able to use what are, conceptually, their own repositories. So Git considers administrators (when operating this way) to own them.

Code in `gix-sec` intends to implement a similar check. But after finding that it is run with an administrative token, it needs to check if the directory is owned by the `Administrators` group, yet instead accidentally examines *itself* again, rather than the directory.

Specifically, in `gix_sec::identity` the [implementation](https://github.com/GitoxideLabs/gitoxide/blob/main/gix-sec/src/identity.rs#L81) of `is_path_owned_by_current_user` for Windows [finds the owner of the directory](https://github.com/GitoxideLabs/gitoxide/blob/ffb73b5f69dbe86ff88f1c473af65f368a6bcbe5/gix-sec/src/identity.rs#L109-L121) (`folder_owner`), [finds the owner of the running thread or process](https://github.com/GitoxideLabs/gitoxide/blob/ffb73b5f69dbe86ff88f1c473af65f368a6bcbe5/gix-sec/src/identity.rs#L151-L189) (`token_owner`), checks cases of ownership not specific to administrators, then attempts to check the administrator-specific case with:

https://github.com/GitoxideLabs/gitoxide/blob/ffb73b5f69dbe86ff88f1c473af65f368a6bcbe5/gix-sec/src/identity.rs#L197-L207

The [`IsWellKnownSid`](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-iswellknownsid) call checks if the owner of the current thread or process is the `Administrators` group. By default, operations carried out when running as an administrator with UAC elevation--or using an administrative account for which UAC is turned off altogether--create not just files and directories with the `Administrators` group as the owner, but other [securable objects](https://learn.microsoft.com/en-us/windows/win32/secauthz/securable-objects) as well, including processes and threads. So this check returns true. (Based on the comment, it may be that this was really meant to check if the *directory* is owned by an administrator. But nothing related to the directory appears in this check.)

The [`CheckTokenMembership`](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-checktokenmembership) call checks if the owner of the current thread or process is an identity enabled in the access token represented by the token handle of `NULL`, passed as `0`. But a token handle of `NULL` represents the running thread. Consequently, if we have gotten this far--which happens when running with full administrative rights--in nearly all situations this will return true as well. (Based on the message, it may be that this was really meant to check if the user is an *administrator*. But nothing related to the `Administrators` group appears in this check.)

### PoC

These examples use `gix fetch` for simplicity, but some other actions implemented in gitoxide are vulnerable, as well as any provided by applications that rely on the results of `gix-sec` checks. 

#### Example 1: From inside a shared or user profile directory

On Windows, running as a limited user account, create a repository in a shared location like `C:\Users\Public`, or even within the limited user's user profile directory. Configure a fake (or, if preferred, real) remote and a value of `core.sshCommand` that runs an arbitrary payload. For example, in PowerShell:

```powershell
git init unsafe-repo
cd unsafe-repo
git remote add origin ssh://localhost/repo.git
git config core.sshCommand 'calc.exe; ssh'
```

Switch from the limited account to an administrative account. Then:

1. If gitoxide is not installed, install it, such as with `cargo install gitoxide`.
2. Run PowerShell with UAC elevation, so that it and processes started in it have an unfiltered token. (If UAC is turned off for this account, then just run PowerShell normally.)
3. This example will not work if the `GIT_SSH_COMMAND` environment variable is set. It is not usually set, but if it may be, you can unset it in the current shell environment by running `$env:GIT_SSH_COMMAND = $null`.
4. `cd` to the limited user's repository as created above.
5. Run `gix fetch`. This runs the Windows calculator (the chosen payload).

#### Example 2: From anywhere

On Windows, even limited user accounts can create directories in the root of the system drive. As a limited user--and assuming the system drive is `C:`--initialize `C:\` itself as a repository. Set up the repository to run the payload, either by editing `C:\.git\config` manually, or by running the `git remote` and `git config` commands from example 1 but passing `-c safe.directory=.`. The second approach is as follows:

```powershell
cd C:\
git init
git -c safe.directory=. remote add origin ssh://localhost/repo.git
git -c safe.directory=. config core.sshCommand 'calc.exe; ssh'
```

(`-c safe.directory=.` keeps `git` from refusing to run the `git remote` and `git config` commands on the repository it has just created, whose `.git` directory is under its control but whose working tree is not.)
 
The entire system drive is now a Git repository due to the presence of `C:\.git`. The limited user owns this `.git` directory and controls the configuration in it. Normally `safe.directory` protections keep this from being a problem. But they are ineffective for administrators running applications (such as the `gix` command) that use `gix-sec` to enforce those protections.

Switch from the limited account to an administrative account. Follow the instructions for the administrator from example 1, except do so from *any* directory anywhere on the `C:` drive that is not in its own repository. Unless `GIT_CEILING_DIRECTORIES` is set in such a way that keeps `C:\` from being considered, running `gix fetch` again runs the Windows calculator. This happens even if the command is run from inside the administrator's own user profile directory.

### Impact

A user is affected only when *all* of the following apply:

- The operating system is Windows.
- The user is a member of the `Administrators` group.
- The program is run with the user's unfiltered token. This happens when UAC is enabled and the user runs the program with UAC elevation, as well as when UAC is disabled. (Running as an administrator but enabling UAC and running the program unelevated is sufficient to avoid this vulnerability.)
- The program uses and relies on information from `gix-sec` about what directories to trust.
- The program interacts with a repository owned by, and set up or controlled by, another user.

Then operations that would run code present in a repository's configuration or hooks when the repository is trusted will be performed in any repository. These operations often require user interaction. But this interaction may not seem to the user like it involves operations on a repository, if it is performed as part of a custom prompt for a shell, or by other software that integrates with repositories. It may also not seem like it involves operation on files controlled by another user, such as when the repository is the root of the system drive.

A malicious user with a limited account on the system may therefore be able to arrange for an administrator to run arbitrary code. However, this vulnerability does not affect cloning repositories or using repositories one has cloned, because cloning does not copy configuration and hooks into the local repository.

The specific attack of making the root of the system drive a repository resembles [CVE-2022-24765](https://github.com/git-for-windows/git/security/advisories/GHSA-vw2c-22j4-2fh2). The workarounds presented there do not work around this vulnerability in full, but would prevent that kind of attack.

## References
- https://github.com/GitoxideLabs/gitoxide/security/advisories/GHSA-7rhf-42qf-vrvc
- https://github.com/GitoxideLabs/gitoxide/commit/39e37482d6f
- https://github.com/GitoxideLabs/gitoxide
