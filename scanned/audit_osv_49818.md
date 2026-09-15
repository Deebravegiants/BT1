# [M] CVE-2019-19451

## Summary
Severity: Medium
Advisory: CVE-2019-19451
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-29
Source: https://osv.dev/vulnerability/CVE-2019-19451
Type: osv

## Details
When GNOME Dia before 2019-11-27 is launched with a filename argument that is not a valid codepoint in the current encoding, it enters an endless loop, thus endlessly writing text to stdout. If this launch is from a thumbnailer service, this output will usually be written to disk via the system's logging facility (potentially with elevated privileges), thus filling up the disk and eventually rendering the system unusable. (The filename can be for a nonexistent file.) NOTE: this does not affect an upstream release, but affects certain Linux distribution packages with version numbers such as 0.97.3.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KTGLGWHINMTDRFL7RZAJZJM5YSVXUXWW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PKLQU2XBM4BGRKOF3L4C5QCPBUNTKEUN/
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00019.html
- https://gitlab.gnome.org/GNOME/dia/issues/428
