# [H] CVE-2021-21374

## Summary
Severity: High
Advisory: CVE-2021-21374
Aliases: GHSA-c2wm-v66h-xhxx
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-26
Source: https://osv.dev/vulnerability/CVE-2021-21374
Type: osv

## Details
Nimble is a package manager for the Nim programming language. In Nim release versions before versions 1.2.10 and 1.4.4, "nimble refresh" fetches a list of Nimble packages over HTTPS without full verification of the SSL/TLS certificate due to the default setting of httpClient. An attacker able to perform MitM can deliver a modified package list containing malicious software packages. If the packages are installed and used the attack escalates to untrusted code execution.

## References
- https://github.com/nim-lang/nimble/blob/master/changelog.markdown#0130
- https://github.com/nim-lang/security/security/advisories/GHSA-c2wm-v66h-xhxx
- https://github.com/nim-lang/Nim/pull/16940
- https://consensys.net/diligence/vulnerabilities/nim-insecure-ssl-tls-defaults-remote-code-execution/
