# [M] Suricata datasets: save to absolute filename can be bypassed when combined with load command

## Summary
Severity: Medium
Advisory: CVE-2026-45767
Aliases: GHSA-gfxq-gffp-w9rv
CVSS: 4.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-45767
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to versions 7.0.16 and 8.0.5, a malicious rule could potentially overwrite any file on the file system on rule load or reload. Versions 7.0.16 and 8.0.5 fix the issue. Some workarounds are available. Preprocess `load`+ `save` rules to disallow absolute filenames for save, use Suricata's privilege dropping to limit writable files, and/or configure landlock in suricata.yaml.

## References
- https://forum.suricata.io/t/suricata-8-0-5-and-7-0-16-released/6315
- https://redmine.openinfosecfoundation.org/issues/8546
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45767.json
- https://github.com/OISF/suricata/security/advisories/GHSA-gfxq-gffp-w9rv
- https://nvd.nist.gov/vuln/detail/CVE-2026-45767
