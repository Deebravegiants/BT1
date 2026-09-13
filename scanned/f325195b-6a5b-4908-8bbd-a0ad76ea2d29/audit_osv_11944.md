# [H] CVE-2018-1000167

## Summary
Severity: High
Advisory: CVE-2018-1000167
Aliases: GHSA-7c4h-w765-6pwg, PYSEC-2018-75
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-18
Source: https://osv.dev/vulnerability/CVE-2018-1000167
Type: osv

## Details
OISF suricata-update version 1.0.0a1 contains an Insecure Deserialization vulnerability in the insecure yaml.load-Function as used in the following files: config.py:136, config.py:142, sources.py:99 and sources.py:131. The "list-sources"-command is affected by this bug. that can result in Remote Code Execution(even as root if suricata-update is called by root). This attack appears to be exploitable via a specially crafted yaml-file at https://www.openinfosecfoundation.org/rules/index.yaml. This vulnerability appears to have been fixed in 1.0.0b1.

## References
- https://redmine.openinfosecfoundation.org/issues/2359
- https://tech.feedyourhead.at/content/remote-code-execution-in-suricata-update
