# [H] CVE-2019-10135

## Summary
Severity: High
Advisory: CVE-2019-10135
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-11
Source: https://osv.dev/vulnerability/CVE-2019-10135
Type: osv

## Details
A flaw was found in the yaml.load() function in the osbs-client versions since 0.46 before 0.56.1. Insecure use of the yaml.load() function allowed the user to load any suspicious object for code execution via the parsing of malicious YAML files.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10135
- https://github.com/containerbuildsystem/osbs-client/pull/865
