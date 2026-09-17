# [C] CVE-2018-1000651

## Summary
Severity: Critical
Advisory: CVE-2018-1000651
CVSS: 10.0 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2018-1000651
Type: osv

## Details
Stroom version <5.4.5 contains a XML External Entity (XXE) vulnerability in XML Parser that can result in disclosure of confidential data, denial of service, server side request forgery, port scanning. This attack appear to be exploitable via Specially crafted XML file.

## References
- https://0dd.zone/2018/08/08/stroom-XXE/
- https://github.com/gchq/stroom/issues/813
