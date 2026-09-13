# [M] CVE-2021-21373

## Summary
Severity: Medium
Advisory: CVE-2021-21373
Aliases: GHSA-8w52-r35x-rgp8
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-03-26
Source: https://osv.dev/vulnerability/CVE-2021-21373
Type: osv

## Details
Nimble is a package manager for the Nim programming language. In Nim release versions before versions 1.2.10 and 1.4.4, "nimble refresh" fetches a list of Nimble packages over HTTPS by default. In case of error it falls back to a non-TLS URL http://irclogs.nim-lang.org/packages.json. An attacker able to perform MitM can deliver a modified package list containing malicious software packages. If the packages are installed and used the attack escalates to untrusted code execution.

## References
- https://github.com/nim-lang/nimble/blob/master/changelog.markdown#0130
- https://github.com/nim-lang/security/security/advisories/GHSA-8w52-r35x-rgp8
- https://consensys.net/diligence/vulnerabilities/nim-insecure-ssl-tls-defaults-remote-code-execution/
