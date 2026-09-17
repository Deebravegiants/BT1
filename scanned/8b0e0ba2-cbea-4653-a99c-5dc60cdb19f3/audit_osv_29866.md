# [H] CVE-2024-47191

## Summary
Severity: High
Advisory: CVE-2024-47191
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-10-09
Source: https://osv.dev/vulnerability/CVE-2024-47191
Type: osv

## Details
pam_oath.so in oath-toolkit 2.6.7 through 2.6.11 before 2.6.12 allows root privilege escalation because, in the context of PAM code running as root, it mishandles usersfile access, such as by calling fchown in the presence of a symlink.

## References
- http://www.openwall.com/lists/oss-security/2024/10/04/2
- http://www.openwall.com/lists/oss-security/2024/10/05/1
- http://www.openwall.com/lists/oss-security/2024/10/08/1
- http://www.openwall.com/lists/oss-security/2024/10/08/2
- http://www.openwall.com/lists/oss-security/2024/10/08/4
- http://www.openwall.com/lists/oss-security/2024/10/15/7
- http://www.openwall.com/lists/oss-security/2024/10/17/1
- http://www.openwall.com/lists/oss-security/2024/10/18/1
- http://www.openwall.com/lists/oss-security/2024/10/18/2
- https://security.opensuse.org/2024/10/04/oath-toolkit-vulnerability.html
- https://www.nongnu.org/oath-toolkit/security/CVE-2024-47191
- https://www.openwall.com/lists/oss-security/2024/10/04/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47191.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47191
- https://gitlab.com/oath-toolkit/oath-toolkit/-/issues/43
- https://gitlab.com/oath-toolkit/oath-toolkit/-/commit/3235a52f6b87cd1c5da6508f421ac261f5e33a70
- https://gitlab.com/oath-toolkit/oath-toolkit/-/commit/3271139989fde35ab0163b558fc29e80c3a280e5
- https://gitlab.com/oath-toolkit/oath-toolkit/-/commit/60d9902b5c20f27e70f8e9c816bfdc0467567e1a
- https://gitlab.com/oath-toolkit/oath-toolkit/-/commit/95ef255e6a401949ce3f67609bf8aac2029db418
