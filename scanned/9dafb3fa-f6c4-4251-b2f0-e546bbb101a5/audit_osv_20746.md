# [M] CVE-2021-3660

## Summary
Severity: Medium
Advisory: CVE-2021-3660
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2022-03-10
Source: https://osv.dev/vulnerability/CVE-2021-3660
Type: osv

## Details
Cockpit (and its plugins) do not seem to protect itself against clickjacking. It is possible to render a page from a cockpit server via another website, inside an <iFrame> HTML entry. This may be used by a malicious website in clickjacking or similar attacks.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1980688
- https://github.com/cockpit-project/cockpit/commit/8d9bc10d8128aae03dfde62fd00075fe492ead10
- https://github.com/cockpit-project/cockpit/issues/16122
