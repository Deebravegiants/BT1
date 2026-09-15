# [H] CVE-2016-3728

## Summary
Severity: High
Advisory: CVE-2016-3728
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-05-20
Source: https://osv.dev/vulnerability/CVE-2016-3728
Type: osv

## Details
Eval injection vulnerability in tftp_api.rb in the TFTP module in the Smart-Proxy in Foreman before 1.10.4 and 1.11.x before 1.11.2 allows remote attackers to execute arbitrary code via the PXE template type portion of the PATH_INFO to tftp/.

## References
- http://projects.theforeman.org/issues/14931
- http://www.openwall.com/lists/oss-security/2016/05/19/2
- http://theforeman.org/security.html#2016-3728
- https://access.redhat.com/errata/RHBA-2016:1501
- https://github.com/theforeman/smart-proxy/commit/eef532aa668d656b9d61d9c6edf7c2505f3f43c7
