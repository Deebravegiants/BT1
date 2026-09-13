# [M] Path Traversal in MISP Object Template Resolution During STIX Import and Export in misp-stix library

## Summary
Severity: Medium
Advisory: CVE-2026-77751
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-77751
Type: osv

## Details
A path traversal vulnerability existed in the handling of MISP object template names during STIX 2 import and MISP-to-STIX 2 export.

MISP object names are passed to PyMISP's object-template resolution mechanism, which constructs a filesystem path by joining the configured MISP object-template directory, the object name, and definition.json. An object name originating from untrusted STIX or MISP content was not sufficiently restricted before being used in this filesystem path.

An attacker able to supply a crafted object name containing path separators or traversal sequences such as ../ could therefore cause template resolution to escape the expected template directory and attempt to load a definition.json file from another location accessible to the process.

During STIX 2 import, an attacker-controlled x_misp_name from a custom STIX object could directly reach this template-resolution mechanism.

The issue could also become persistent. A malicious object name stored in a MISP event could later be processed again during STIX 2 export. Consequently, content originally introduced in one security context could trigger filesystem access later when the event is exported by a process operating with different or greater privileges.

If a suitable definition.json file exists outside the intended template directory, its contents may be interpreted as a MISP object template and fields from that file copied into the converted object. This can result in unintended disclosure of locally accessible data represented by the template file and modification of the resulting object's metadata or semantics.

The patches introduce strict validation of object-template names. Valid names are restricted to a single path component containing letters, digits, hyphens, or underscores. Names that do not meet these requirements are replaced with the generic unknown-template name before reaching PyMISP template resolution. The original rejected name is preserved in the object's comment and a warning is generated, preventing traversal while retaining the source information.

## References
- https://github.com/MISP/misp-stix/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77751.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-77751
- https://github.com/MISP/misp-stix/commit/a0f54070
- https://github.com/MISP/misp-stix/commit/a8b6808d
