# [H] Data written to GitHub Actions Cache may expose secrets

## Summary
Severity: High
Advisory: GHSA-h3qr-39j9-4r5v
CVE: CVE-2023-30853
CWE: CWE-200, CWE-312
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2023-05-01
Source: https://github.com/advisories/GHSA-h3qr-39j9-4r5v
Type: github-advisory

## Affected
- GitHub Actions: `gradle/gradle-build-action` — affected >=0 <2.4.2

## Details
### Impact

This vulnerability impacts GitHub workflows using the [Gradle Build Action](https://github.com/marketplace/actions/gradle-build-action) that have executed the Gradle Build Tool with the [configuration cache](https://docs.gradle.org/current/userguide/configuration_cache.html) enabled, potentially exposing secrets configured for the repository.

Secrets configured for GitHub Actions are normally passed to the Gradle Build Tool via environment variables. Due to the way that the Gradle Build Tool records these environment variables, they may be persisted into an entry in the GitHub Actions cache. This data stored in the GitHub Actions cache can be read by a GitHub Actions workflow running in an untrusted context, such as that running for a Pull Request submitted by a developer via a repository fork.

This vulnerability was discovered internally through code review, and we have not seen any evidence of it being exploited in the wild. However, in addition to upgrading the Gradle Build Action, you should delete any potentially vulnerable cache entries and may choose to rotate any potentially affected secrets ([see Remediation](#Remediation)).

### Patches

[Gradle Build Action v2.4.2](https://github.com/gradle/gradle-build-action/releases/tag/v2.4.2) (and newer) no longer save this sensitive data for later use, preventing ongoing leakage of secrets via the GitHub Actions Cache. We strongly recommend that all users of the Gradle Build Action upgrade to `v2.4.2` (or simply `v2`) immediately.

### Remediation

While upgrading to the latest version of the Gradle Build Action will prevent leakage of secrets going forward, additional actions may be required due to current or previous GitHub Actions Cache entries containing this information.

Current cache entries will remain vulnerable until they are forcibly deleted or they expire naturally after 7 days of not being used. Potentially vulnerable entries can be easily identified in the GitHub UI by searching for a cache entry with key matching `configuration-cache-*`. We recommend that users of the Gradle Build Action inspect their list of cache entries and [manually delete any that match this pattern](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows#deleting-cache-entries).

While we have not seen any evidence of this vulnerability being exploited, we recommend cycling any repository secrets if you cannot be certain that these have not been compromised. Compromise could occur if you run a GitHub Actions workflow for a pull request attempting to exploit this data. 
Warning signs to look for in a pull request include:
- Making changes to GitHub Actions workflow files in a way that may attempt to read/extract data from the Gradle User Home or <project-root>/.gradle directories.
- Making changes to Gradle build files or other executable files that may be invoked by a GitHub Actions workflow, in a way that may attempt to read/extract information from these locations.

### Workarounds

We strongly recommend that all users upgrade to the latest version of the Gradle Build Action as soon as possible, and delete any potentially vulnerable cache entries from the GitHub Actions cache ([see Remediation](#Remediation)). 

If for some reason this is not possible, users can limit the impact of this vulnerability:
- If the Gradle project does not opt-in to using the configuration cache, then it is not vulnerable. 
- If the Gradle project does opt-in to using the configuration-cache by default, then the `--no-configuration-cache` command-line argument can be used to disable this feature in a GitHub Actions workflow.

In any case, we recommend that users carefully inspect any pull request before approving the execution of GitHub Actions workflows. It may be prudent to require approval for all PRs from external contributors, as described [here](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository#controlling-changes-from-forks-to-workflows-in-public-repositories).

## References
- https://github.com/gradle/gradle-build-action/security/advisories/GHSA-h3qr-39j9-4r5v
- https://nvd.nist.gov/vuln/detail/CVE-2023-30853
- https://github.com/gradle/gradle-build-action
- https://github.com/gradle/gradle-build-action/releases/tag/v2.4.2
