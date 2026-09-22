# [C] YAML::Syck versions through 1.36 for Perl has several potential security vulnerabilities including a high-severity heap buffer overflow in the YAML emitter

## Summary
Severity: Critical
Advisory: CVE-2026-4177
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/CVE-2026-4177
Type: osv

## Details
YAML::Syck versions through 1.36 for Perl has several potential security vulnerabilities including a high-severity heap buffer overflow in the YAML emitter.

The heap overflow occurs when class names exceed the initial 512-byte allocation.

The base64 decoder could read past the buffer end on trailing newlines.

strtok mutated n->type_id in place, corrupting shared node data.

A memory leak occurred in syck_hdlr_add_anchor when a node already had an anchor. The incoming anchor string 'a' was leaked on early return.

## References
- http://www.openwall.com/lists/oss-security/2026/03/16/6
- https://cpan.org/modules
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-4177.json
- https://access.redhat.com/errata/RHSA-2026:6470
- https://access.redhat.com/errata/RHSA-2026:8311
- https://access.redhat.com/security/cve/CVE-2026-4177
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4177.json
- https://metacpan.org/release/TODDR/YAML-Syck-1.37_01/changes#L21
- https://nvd.nist.gov/vuln/detail/CVE-2026-4177
- https://bugzilla.redhat.com/show_bug.cgi?id=2448277
- https://github.com/cpan-authors/YAML-Syck/commit/e8844a31c8cf0052914b198fc784ed4e6b8ae69e.patch
- https://github.com/cpan-authors/YAML-Syck
