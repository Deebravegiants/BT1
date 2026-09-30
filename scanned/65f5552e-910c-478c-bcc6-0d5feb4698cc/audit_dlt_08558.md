# [?] Describe how to report vulnerabilities in CONTRIBUTING.md. (#22)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2019-06-14
Source: https://github.com/algorand/go-algorand/commit/dde4f1bca74d4a9b9b3b8b55ab237efac82df56a
Type: security-commit

## Details
Describe how to report vulnerabilities in CONTRIBUTING.md. (#22)

Link to the Algorand vulnerability submission form and bug bounty program.

## Patch
### CONTRIBUTING.md
```diff
@@ -6,21 +6,31 @@ The algorand project is composed of several repositories on GitHub. Specifically
 
 # Filing Issues
 
-Did you discover a bug? Do you have a feature request? Filing issues is an easy way anyone can contribute and helps us improve Algorand. We use GitHub  Issues to track all known bugs and feature requests. 
+Did you discover a bug? Do you have a feature request? Filing issues is an easy way anyone can contribute and helps us improve Algorand. We use GitHub Issues to track all known bugs and feature requests.
 
 Before logging an issue be sure to check current issues, verify that your [node is synced](https://developer.algorand.org/docs/introduction-installing-node#sync-node), check the [Developer Frequently Asked Questions](https://developer.algorand.org/docs/developer-faq) and [GitHub issues][issues_url] to see if your issue is described there.
 
 If you’d like to contribute to any of the repositories, please file a [GitHub issue][issues_url] using the issues menu item. Make sure to specify whether you are describing a bug or a new enhancement using the **Bug report** or **Feature request** button.
 
-See the GitHub help guide for more information on [filing an issue](https://help.github.com/en/articles/creating-an-issue)
+See the GitHub help guide for more information on [filing an issue](https://help.github.com/en/articles/creating-an-issue).
+
+## Vulnerabilities
+
+Please don't create issues for any security vulnerabilities.  Instead, we would appreciate it if you reported them through our [vulnerability disclosure form][vuln_url].  This allows us to distribute a fix before the vulnerability is exploited.
+
+Additionally, if you believe that you've discovered a security vulnerability, you might qualify for our bug bounty program.  Visit our [bug bounty site][bug_bounty_url] for details.
+
+If you have any questions, don't hesitate to contact us at security@algorand.com.
 
 # Contribution Model
 
 For each of our repositories we use the same model for contributing code. Developers wanting to contribute must create pull requests. This process is described in the GitHub [Creating a pull request from a fork](https://help.github.com/en/articles/creating-a-pull-request-from-a-fork) documentation. Each pull request should be initiated against the master branch in the Algorand repository.  After a pull request is submitted the core development team will review the submission and communicate with the developer using the comments sections of the PR. After the submission is reviewed and approved, it will be merged into the master branch of the source. These changes will be merged to our release branch on the next viable release date. For the SDKs, this may be immediate. Changes to the node software may take more time as we must ensure and verify the security, as well as apply protocol upgrades in an orderly way.
 
+Again, if you have a patch for a critical security vulnerability, please use our [vulnerability disclosure form][vuln_url] instead of creating a PR.  We'll follow up with you on distributing the patch before we merge it.
+
 # Code Guidelines
 
-For Go code we use the [Golang guidelines defined here](https://golang.org/doc/effective_go.html)
+For Go code we use the [Golang guidelines defined here](https://golang.org/doc/effective_go.html).
 * Code must adhere to the official Go formatting guidelines (i.e. uses gofmt).
 * We use **gofmt** and **golint**. Also make sure to run `make fix` and `make generate` before opening a pull request.
 * Code must be documented adhering to the official Go commentary guidelines.
@@ -34,3 +44,5 @@ For Java code we use [Oracle’s standard formatting rules for Java](https://www
 The core development team monitors the Algorand community forums and regularly responds to questions and suggestions. Issues and Pull Requests are handled on GitHub.
 
 [issues_url]: https://github.com/algorand/go-algorand/issues
+[vuln_url]: https://www.algorand.com/resources/blog/security
+[bug_bounty_url]: https://bugcrowd.com/algorand
```
