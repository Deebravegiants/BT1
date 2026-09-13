# [H] CVE-2014-9938

## Summary
Severity: High
Advisory: CVE-2014-9938
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2014-9938
Type: osv

## Details
contrib/completion/git-prompt.sh in Git before 1.9.3 does not sanitize branch names in the PS1 variable, allowing a malicious repository to cause code execution.

## References
- https://access.redhat.com/errata/RHSA-2017:2004
- https://github.com/git/git/commit/8976500cbbb13270398d3b3e07a17b8cc7bff43f
- https://github.com/njhartwell/pw3nage
- https://github.com/njhartwell/pw3nage
- https://github.com/git/git/commit/8976500cbbb13270398d3b3e07a17b8cc7bff43f
