# [M] CVE-2021-3639

## Summary
Severity: Medium
Advisory: CVE-2021-3639
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2022-08-22
Source: https://osv.dev/vulnerability/CVE-2021-3639
Type: osv

## Details
A flaw was found in mod_auth_mellon where it does not sanitize logout URLs properly. This issue could be used by an attacker to facilitate phishing attacks by tricking users into visiting a trusted web application URL that redirects to an external and potentially malicious server. The highest threat from this liability is to confidentiality and integrity.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1980648
- https://access.redhat.com/security/cve/CVE-2021-3639
- https://github.com/latchset/mod_auth_mellon/commit/42a11261b9dad2e48d70bdff7c53dd57a12db6f5
