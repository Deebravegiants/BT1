# [H] CVE-2021-4213

## Summary
Severity: High
Advisory: CVE-2021-4213
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-24
Source: https://osv.dev/vulnerability/CVE-2021-4213
Type: osv

## Details
A flaw was found in JSS, where it did not properly free up all memory. Over time, the wasted memory builds up in the server memory, saturating the server’s RAM. This flaw allows an attacker to force the invocation of an out-of-memory process, causing a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2021-4213
- https://security-tracker.debian.org/tracker/CVE-2021-4213
- https://bugzilla.redhat.com/show_bug.cgi?id=2042900
- https://github.com/dogtagpki/jss/commit/3aabe0e9d59b0a42e68ac8cd0468f9c5179967d2
- https://github.com/dogtagpki/jss/commit/5922560a78d0dee61af8a33cc9cfbf4cfa291448
