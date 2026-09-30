# [?] docs: Added maintainability section, to include vulnerability checking (#2755)

## Summary
Severity: Unknown
Chain: Cosmos Hub
Component: cosmos/gaia
Published: 2023-09-28
Source: https://github.com/cosmos/gaia/commit/cb8f5d868483a0596159d21b9f8d7bf5d26e213f
Type: security-commit

## Details
docs: Added maintainability section, to include vulnerability checking (#2755)

* Added maintainability section, to include vulnerability checking

* Updated with review comments

## Patch
### docs/guidelines/code-guidelines.md
```diff
@@ -8,6 +8,20 @@ This documents idiomatic conventions in the Go code that we follow for gaia deve
 2. [Go Common Mistakes](https://github.com/golang/go/wiki/CommonMistakes)
 3. [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
 
+## Maintainability
+
+From a maintainance, performance and security perspective, it is important to keep the footprint of the `gaiad` application as lean as possible.
+
+When adding any new feature, you must ensure that any libraries you wish to include are well maintained and have sufficient usage in the wider ecosystem. This is necessary to avoid having to rework the `gaiad` application at a later date, if a library is no longer maintained or is abandoned by its core contributors.
+
+In addition to the above, if any library is to be included, it is necessary to check that the version used does not have any known vunerabilities. As a developer working on a feature, before making a pull request, ensure that you run, along with the testing targets, the vulnerability checking target in the root of the gaia repository directory:
+
+```sh
+make govulncheck
+```
+
+The above command will run the vulnerability checker that will detail any known issues for the library version that your using. If any issues are raised, or you have any concerns, please reach out to the core-developers who will be able to advise further.
+
 ## Run tests
 
 - Run unit tests
@@ -36,7 +50,7 @@ make docker-build-debug && \
 make test-e2e
 ```
 
-# Guidelines
+## Guidelines
 
 These guidelines are the conventions that govern our code. These conventions cover far more than just source file formatting. Can `gofmt` and `goimports` handle that for us.
 
@@ -45,6 +59,7 @@ The goal of this guide is to manage this complexity by describing in detail the
 Try to avoid extensive methods and always test your code. All PRs should have at least 95% of code coverage.
 
 - [Contributing](#contributing)
+  - [Maintainability](#maintainability)
   - [Run tests](#run-tests)
 - [Guidelines](#guidelines)
   - [Project organization](#project-organization)
@@ -95,6 +110,7 @@ Try to avoid extensive methods and always test your code. All PRs should have at
       - [Use Subtests](#use-subtests)
     - [Avoid writing directly in the stdout](#avoid-writing-directly-in-the-stdout)
     - [Avoid panic](#avoid-panic)
+  - [Security](#security)
 
 ## Project organization
 
@@ -1333,5 +1349,4 @@ It's also easier to maintain. We don't need to find all prints and change the co
 ### Avoid panic
 
 Avoid panic in simple and small methods; all errors should be handled on the top level and application, and we can decide if we will panic or not.
-We can also create a proper panic recovery to close all states, open connection from the application, and graceful exit without breaking anything. 
-
+We can also create a proper panic recovery to close all states, open connection from the application, and graceful exit without breaking anything.
```
