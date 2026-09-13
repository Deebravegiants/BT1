# [H] CVE-2017-6967

## Summary
Severity: High
Advisory: CVE-2017-6967
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2017-03-17
Source: https://osv.dev/vulnerability/CVE-2017-6967
Type: osv

## Details
xrdp 0.9.1 calls the PAM function auth_start_session() in an incorrect location, leading to PAM session modules not being properly initialized, with a potential consequence of incorrect configurations or elevation of privileges, aka a pam_limits.so bypass.

## References
- https://bugs.launchpad.net/ubuntu/+source/xrdp/+bug/1672742
- https://github.com/neutrinolabs/xrdp/issues/350
- https://github.com/neutrinolabs/xrdp/pull/694
