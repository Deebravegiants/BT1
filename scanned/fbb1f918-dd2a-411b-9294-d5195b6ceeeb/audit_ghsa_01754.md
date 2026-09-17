# [C] GitHub personal access token leaking into temporary EasyBuild (debug) logs

## Summary
Severity: Critical
Advisory: GHSA-2wx6-wc87-rmjm
CVE: CVE-2020-5262
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2020-03-19
Source: https://github.com/advisories/GHSA-2wx6-wc87-rmjm
Type: github-advisory

## Affected
- PyPI: `easybuild-framework` — affected >=0 <4.1.2

## Details
### Impact

The GitHub Personal Access Token (PAT) used by EasyBuild for the GitHub integration features (like `--new-pr`, `--from-pr`, etc.) is shown in plain text in EasyBuild debug log files.

Scope:

* the log message only appears in the top-level log file, *not* in the individual software installation logs (see https://easybuild.readthedocs.io/en/latest/Logfiles.html);
    - as a consequence, tokens are *not* included in the partial log files that are uploaded into a gist when using `--upload-test-report` in combination with `--from-pr`, nor in the installation logs that are copied to the software installation directories;
* the message is only logged when using `--debug`, so it will not appear when using the default EasyBuild configuration (only info messages are logged by default);
* the log message is triggered via `--from-pr`, but also via various other GitHub integration options like `--new-pr`, `--merge-pr`, `--close-pr`, etc., but usually only appears in the temporary log file that is cleaned up automatically as soon as eb completes successfully;
* you may have several debug log files that include your GitHub token in `/tmp` (or a different location if you've set the `--tmpdir` EasyBuild configuration option) on the systems where you use EasyBuild, but they are located in a subdirectory that is only accessible to your account (permissions set to 700);
* the only way that a log file that may include your token could have been made public is *if you shared it yourself*, for example by copying the contents of the log file into a gist manually, or by sending a log file to someone;
* for log files uploaded to GitHub, your token would be revoked automatically when GitHub notices it;

### Patches

The issue is fixed with the changes in https://github.com/easybuilders/easybuild-framework/pull/3248.

This fix is included in EasyBuild v4.1.2 (released on Mon Mar 16th 2020), and in the `master`+  `develop` branches of the `easybuild-framework` repository since Mon Mar 16th 2020 (see https://github.com/easybuilders/easybuild-framework/pull/3248 and https://github.com/easybuilders/easybuild-framework/pull/3249 resp.).

**Make sure you revoke the existing GitHub tokens you're using with EasyBuild** (via https://github.com/settings/tokens), and install new ones using "`eb --install-github-token --force`" (see also https://easybuild.readthedocs.io/en/latest/Integration_with_GitHub.html#installing-a-github-token-install-github-token).

### Workarounds

* avoid using the GitHub integration features (see https://easybuild.readthedocs.io/en/latest/Integration_with_GitHub.html) with EasyBuild versions older than version 4.1.2;
* don't share top-level EasyBuild (debug) log files with others, unless you are sure your GitHub token is not included in them;
* clean up temporary EasyBuild log files in `/tmp`on the system(s) where you`re using EasyBuild

### References

* https://github.com/easybuilders/easybuild-framework/pull/3248 (PR that fixes the issue)
* (release announcement to EasyBuild mailing list)

### For more information

* Open an issue in [the `easybuild-framework` repository](https://github.com/easybuilders/easybuild-framework)
* Email us at [easybuild-admin@lists.ugent.be](mailto:easybuild-admin@lists.ugent.be)

## References
- https://github.com/easybuilders/easybuild-framework/security/advisories/GHSA-2wx6-wc87-rmjm
- https://nvd.nist.gov/vuln/detail/CVE-2020-5262
- https://github.com/easybuilders/easybuild-framework/pull/3248
- https://github.com/easybuilders/easybuild-framework/pull/3249
- https://github.com/easybuilders/easybuild-framework/commit/210743d0e3618a8ac0a56eb9c0f4fa4fd8ae53b9
- https://github.com/easybuilders/easybuild-framework
- https://github.com/pypa/advisory-database/tree/main/vulns/easybuild-framework/PYSEC-2020-41.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/easybuild/PYSEC-2020-268.yaml
