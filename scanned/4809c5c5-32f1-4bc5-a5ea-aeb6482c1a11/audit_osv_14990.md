# [C] CVE-2019-12835

## Summary
Severity: Critical
Advisory: CVE-2019-12835
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-15
Source: https://osv.dev/vulnerability/CVE-2019-12835
Type: osv

## Details
formats/xml.cpp in Leanify 0.4.3 allows for a controlled out-of-bounds write in xml_memory_writer::write via characters that require escaping.

## References
- https://github.com/JayXon/Leanify/issues/52
