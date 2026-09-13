# [C] CVE-2021-32692

## Summary
Severity: Critical
Advisory: CVE-2021-32692
Aliases: GHSA-3x6w-q32m-jqf3
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-12-23
Source: https://osv.dev/vulnerability/CVE-2021-32692
Type: osv

## Details
Activity Watch is a free and open-source automated time tracker. Versions prior to 0.11.0 allow an attacker to execute arbitrary commands on any macOS machine with ActivityWatch running. The attacker can exploit this vulnerability by having the user visiting a website with the page title set to a malicious string. An attacker could use another application to accomplish the same, but the web browser is the most likely attack vector. This issue is patched in version 0.11.0. As a workaround, users can run the latest version of aw-watcher-window from source, or manually patch the `printAppTitle.scpt` file.

## References
- https://github.com/ActivityWatch/activitywatch/security/advisories/GHSA-3x6w-q32m-jqf3
