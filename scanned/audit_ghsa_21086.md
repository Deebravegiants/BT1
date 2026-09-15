# [C] check-spelling workflow vulnerable to token leakage via symlink attack

## Summary
Severity: Critical
Advisory: GHSA-g86g-chm8-7r2p
CVE: CVE-2021-32724
CWE: CWE-532
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2022-07-29
Source: https://github.com/advisories/GHSA-g86g-chm8-7r2p
Type: github-advisory

## Affected
- GitHub Actions: `check-spelling/check-spelling` — affected >=0 <0.0.19

## Details
### Impact
For a repository with the [check-spelling action](https://github.com/marketplace/actions/check-spelling) enabled that triggers on `pull_request_target` (or `schedule`), an attacker can send a crafted Pull Request that causes a `GITHUB_TOKEN` to be exposed.

With the `GITHUB_TOKEN`, it's possible to push commits to the repository bypassing standard approval processes. Commits to the repository could then steal any/all secrets available to the repository.

### Workarounds

You can either:
* [Disable the workflow](https://docs.github.com/en/actions/managing-workflow-runs/disabling-and-enabling-a-workflow) until you've fixed **all branches**.  

or
* Set repository to [Allow specific actions](https://docs.github.com/en/github/administering-a-repository/managing-repository-settings/disabling-or-limiting-github-actions-for-a-repository#allowing-specific-actions-to-run). You can check: 
   - [x] `Allow actions created by GitHub`
   - [x] `Allow Marketplace actions by verified creators`

[check-spelling](https://github.com/check-spelling) isn't a verified creator and it certainly won't be anytime soon. You could then explicitly add other actions that your repository uses.

or
* Set repository [Workflow permissions](https://docs.github.com/en/github/administering-a-repository/managing-repository-settings/disabling-or-limiting-github-actions-for-a-repository#setting-the-permissions-of-the-github_token-for-your-repository) to `Read repository contents permission`.

### Solution

Workflows using `check-spelling/check-spelling@main` were fixed automatically with the release of [v0.0.19](https://github.com/check-spelling/check-spelling/releases/tag/v0.0.19).

Workflows using a pinned sha or tagged version will need to change the affected workflows for *all* repository branches to the latest version.

#### The simple case

In the simple case, you have few enough open branches that you can do the following on **all branches**.

- Edit the workflow to use `check-spelling/check-spelling@main`, or
- Edit the workflow to use `check-spelling/check-spelling@v0.0.19`, or
- Delete the workflow file, or
- Change the workflow to only use `on: push`
  - this will result in PRs losing status checks (commits will still have statuses)

#### The complex case

If you have too many open branches to feasibly fix all of them as per the above, you can instead do the following:

1. Perform the above solution on all open branches for which you need `check-spelling` to be active.
2. On all open branches on which you need `check-spelling` to be active, rename the workflow file (e.g. to `spelling2.yml`)
3. On the default branch, create a dummy workflow file with the old name (this is usually `spelling.yml`).
4. Use the GitHub Actions UI to disable the workflow with the old name (this is usually `spelling.yml`).

This should prevent the vulnerable workflow from executing on any branches that you have not applied the proper solution to.

The reason for creating the dummy file (Step 3) before disabling the workflow (Step 4) is that, in our testing, GitHub may un-disable a workflow if it does not exist on your default branch.

Example dummy workflow file (For step 3):

```yml
# spelling.yml is disabled per https://github.com/check-spelling/check-spelling/security/advisories/GHSA-g86g-chm8-7r2p
name: Workflow should not run!
on:
  push:
    branches: ''

jobs:
  placeholder:
    name: Should be disabled
    runs-on: ubuntu-latest
    if: false
    steps:
    - name: Task
      run: |
        echo 'Running this task would be bad'
        exit 1
```

You *should also* include a comment in the new workflow to remind people not to resurrect the old name, for example:

```yml
# spelling.yml is disabled per https://github.com/check-spelling/check-spelling/security/advisories/GHSA-g86g-chm8-7r2p
```

Finally, you should consider sending a Pull Request to an open branch in which you have not performed the proper solution to verify that the old version of `check-spelling` does not execute.

#### How to upgrade

Perform this change to your impacted workflow file (typically `.github/workflows/spelling.yml`):
```diff
@@ -24 +24 @@
-    - uses: check-spelling/check-spelling@v0.0.18
+    - uses: check-spelling/check-spelling@v0.0.19
```

As noted above, if you have many branches, you should additionally rename the workflow and include a comment to remind people not to use the old workflow file name:
```
# spelling.yml is blocked per https://github.com/check-spelling/check-spelling/security/advisories/GHSA-g86g-chm8-7r2p
```

### Reviewing workflow runs

Users can verify who and which Pull Requests have been running the action by looking up the spelling.yml action in the Actions tab of their repositories, e.g., https://github.com/check-spelling/check-spelling/actions/workflows/spelling.yml - you can filter PRs by adding `?query=event%3Apull_request_target`, e.g., https://github.com/check-spelling/check-spelling/actions/workflows/spelling.yml?query=event%3Apull_request_target.


### References

* For more information on `pull_request_target` attacks, see [GitHub Security Lab: Keeping your GitHub Actions and workflows secure: Preventing pwn requests](https://securitylab.github.com/research/github-actions-preventing-pwn-requests/)
* For information on workflow hardening techniques, see [GitHub: Security hardening for GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/security-hardening-for-github-actions)

### Credit
Thanks to [@justinsteven](https://twitter.com/justinsteven) for reporting as well as in helping validate the fix.

### For more information

For questions or comments about this advisory:
* Email us at [check-spelling@check-spelling.dev](mailto:check-spelling@check-spelling.dev)

## References
- https://github.com/check-spelling/check-spelling/security/advisories/GHSA-g86g-chm8-7r2p
- https://nvd.nist.gov/vuln/detail/CVE-2021-32724
- https://github.com/check-spelling/check-spelling/commit/436362fc6b588d9d561cbdb575260ca593c8dc56
- https://github.com/check-spelling/check-spelling
- https://github.com/check-spelling/check-spelling/releases/tag/v0.0.19
