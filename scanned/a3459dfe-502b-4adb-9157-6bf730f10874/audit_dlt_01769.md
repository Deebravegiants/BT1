# [?] Convert issue templates to forms. Add new security issue form. (#4271)

## Summary
Severity: Unknown
Chain: Cardano
Component: IntersectMBO/plutus
Published: 2021-12-09
Source: https://github.com/IntersectMBO/plutus/commit/9db2c60e1eab216e2b050ce560cd36be7ad78ec4
Type: security-commit

## Details
Convert issue templates to forms. Add new security issue form. (#4271)

* Convert issue templates to forms. Add new weakness issue form.

* Update issue forms

* Update forms

* Correct links in issue forms

## Patch
### .github/ISSUE_TEMPLATE/bug_report.md
```diff
@@ -1,53 +0,0 @@
----
-name: Bug report
-about: Report a bug
-title: ""
-labels: bug
-assignees: ''
-
----
-<!--
-IMPORTANT
-
-This repository used to contain the code for the Plutus Application Framework and Marlowe.
-These have now *moved*:
-
-- [Plutus Application Framework](https://github.com/input-output-hk/plutus-apps)
-- [Marlowe](https://github.com/input-output-hk/marlowe-cardano)
-
-Please ensure that you make your issue in the appropriate repository!
--->
-
-## Summary
-
-A clear and specific description of what the bug is.
-
-## Steps to reproduce
-
-Steps to reproduce the behavior:
-1. Go to '...'
-2. Click on '....'
-3. Scroll down to '....'
-4. See error
-
-## Expected behavior
-
-A clear and concise description of what you expected to happen.
-
-## System info (please complete the following information):
-
-- OS: [e.g. Ubuntu]
-- Version [e.g. 20.04]
-- Plutus version or commit hash
-
-## Screenshots and attachments
-
-If applicable, add screenshots, config files and/or logs to help explain the problem.
-
-## Describe the approach you would take to fix this 
-
-If you would like to work on this yourself (optional!), then let us know what approach you would take so we can advise you.
-
-## Additional context
-
-Add any other context about the problem here.
```

### .github/ISSUE_TEMPLATE/bug_report.yml
```diff
@@ -0,0 +1,65 @@
+name: Bug Report
+description: Report a bug
+#title: ""
+labels: ["bug"]
+#assignees:
+#  -
+body:
+  - type: markdown
+    attributes:
+      value: |
+        Thanks for taking the time to fill out this bug report.
+        Please check the existing issues, [Plutus Docs](https://plutus.readthedocs.io/en/latest/) and [Cardano Stack Exchange](https://cardano.stackexchange.com/) before raising.
+  - type: textarea
+    id: summary
+    attributes:
+      label: Summary
+      description: |
+        A clear and specific description of what the bug is.
+        If applicable, add screenshots, config files and/or logs to help explain the problem.
+    validations:
+      required: true
+  - type: textarea
+    id: steps-to-reproduce
+    attributes:
+      label: Steps to reproduce the behavior
+      placeholder: |
+        1. Go to '...'
+        2. Click on '...'
+        3. Scroll down to '...'
+    validations:
+      required: true
+  - type: textarea
+    id: actual-result
+    attributes:
+      label: Actual Result
+      description: What is the reproducible outcome?
+      placeholder: See error...
+    validations:
+      required: true
+  - type: textarea
+    id: expected-result
+    attributes:
+      label: Expected Result
+      description: A clear and concise description of what you expected to happen.
+      placeholder: No errors observed.
+    validations:
+      required: true
+  - type: textarea
+    id: fix-it-yourself
+    attributes:
+      label: Describe the approach you would take to fix this 
+      description: If you would like to work on this yourself (optional!), then let us know what approach you would take so we can advise you.
+    validations:
+      required: false
+  - type: textarea
+    id: system-info
+    attributes:
+      label: System info
+      placeholder: |
+        OS: [e.g. Ubuntu]
+        Version: [e.g. 20.04]
+        Plutus: version or commit hash
+    validations:
+      required: true
+
```

### .github/ISSUE_TEMPLATE/feature_request.md
```diff
@@ -1,35 +0,0 @@
----
-name: Feature request
-about: Submit a feature request
-title: ""
-labels: enhancement
-assignees: ''
-
----
-<!--
-IMPORTANT
-
-This repository used to contain the code for the Plutus Application Framework and Marlowe.
-These have now *moved*:
-
-- [Plutus Application Framework](https://github.com/input-output-hk/plutus-apps)
-- [Marlowe](https://github.com/input-output-hk/marlowe-cardano)
-
-Please ensure that you make your issue in the appropriate repository!
--->
-
-## Describe the feature you'd like
-
-A clear and detailed description of what you are suggesting.
-
-## Describe alternatives you've considered
-
-A clear and concise description of any alternative solutions or features you've considered.
-
-## Describe the approach you would take to implement this 
-
-If you would like to work on this yourself (optional!), then let us know what approach you would take so we can advise you.
-
-## Additional context / screenshots
-
-Add any other context or screenshots about the feature request here.
```

### .github/ISSUE_TEMPLATE/feature_request.yml
```diff
@@ -0,0 +1,26 @@
+name: Feature Request
+description: Submit a feature request
+#title: ""
+labels: ["enhancement"]
+#assignees:
+#  -
+body:
+  - type: markdown
+    attributes:
+      value: |
+        Thanks for taking the time to fill out this feature request.
+        Please check the existing issues, [Plutus Docs](https://plutus.readthedocs.io/en/latest/) and [Cardano Stack Exchange](https://cardano.stackexchange.com/) before raising.
+  - type: textarea
+    id: description
+    attributes:
+      label: Describe the feature you'd like
+      description: A clear and detailed description of what you are suggesting.
+    validations:
+      required: true
+  - type: textarea
+    id: alternatives
+    attributes:
+      label: Describe alternatives you've considered
+      description: A clear and concise description of any alternative solutions or features you've considered.
+    validations:
+      required: false
\ No newline at end of file
```

### .github/ISSUE_TEMPLATE/security_report.yml
```diff
@@ -0,0 +1,37 @@
+name: Security Report
+description: Report a security issue
+#title: ""
+labels: ["security"]
+#assignees:
+#  -
+body:
+  - type: markdown
+    attributes:
+      value: |
+        Thanks for taking the time to fill out this security report.
+        Please check the existing issues, [Plutus Docs](https://plutus.readthedocs.io/en/latest/) and [Cardano Stack Exchange](https://cardano.stackexchange.com/) before raising.
+  - type: textarea
+    id: summary
+    attributes:
+      label: Summary
+      description: A clear and specific description of what the issue is
+    validations:
+      required: true
+  - type: textarea
+    id: proposed-solution
+    attributes:
+      label: Do you have a proposed solution for this issue?
+      description: Describe what solutions you've considered
+    validations:
+      required: false
+  - type: textarea
+    id: system-info
+    attributes:
+      label: System info
+      placeholder: |
+        OS: [e.g. Ubuntu]
+        Version: [e.g. 20.04]
+        Plutus: version or commit hash
+    validations:
+      required: false
+
```
