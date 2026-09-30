# [H] CVE-2017-8929

## Summary
Severity: High
Advisory: CVE-2017-8929
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-14
Source: https://osv.dev/vulnerability/CVE-2017-8929
Type: osv

## Details
The sized_string_cmp function in libyara/sizedstr.c in YARA 3.5.0 allows remote attackers to cause a denial of service (use-after-free and application crash) via a crafted rule.

## References
- https://github.com/VirusTotal/yara/commit/053e67e3ec81cc9268ce30eaf0d6663d8639ed1e
- https://github.com/VirusTotal/yara/issues/658
