# [H] CVE-2021-22539

## Summary
Severity: High
Advisory: CVE-2021-22539
Aliases: GHSA-2rcw-j8x4-hgcv
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-04-16
Source: https://osv.dev/vulnerability/CVE-2021-22539
Type: osv

## Details
An attacker can place a crafted JSON config file into the project folder pointing to a custom executable. VScode-bazel allows the workspace path to lint *.bzl files to be set via this config file. As such the attacker is able to execute any executable on the system through vscode-bazel. We recommend upgrading to version 0.4.1 or above.

## References
- https://github.com/bazelbuild/vscode-bazel/security/advisories/GHSA-2rcw-j8x4-hgcv
- https://github.com/bazelbuild/vscode-bazel-ghsa-2rcw-j8x4-hgcv/pull/1
