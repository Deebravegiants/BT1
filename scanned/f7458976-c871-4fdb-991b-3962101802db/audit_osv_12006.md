# [H] CVE-2018-1000622

## Summary
Severity: High
Advisory: CVE-2018-1000622
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-09
Source: https://osv.dev/vulnerability/CVE-2018-1000622
Type: osv

## Details
The Rust Programming Language rustdoc version Between 0.8 and 1.27.0 contains a CWE-427: Uncontrolled Search Path Element vulnerability in rustdoc plugins that can result in local code execution as a different user. This attack appear to be exploitable via using the --plugin flag without the --plugin-path flag. This vulnerability appears to have been fixed in 1.27.1.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00076.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00031.html
- https://groups.google.com/forum/#%21topic/rustlang-security-announcements/4ybxYLTtXuM
- https://security.gentoo.org/glsa/201812-11
