# [C] CVE-2020-24715

## Summary
Severity: Critical
Advisory: CVE-2020-24715
Aliases: GHSA-738x-v49g-p6hx, PYSEC-2020-252
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-27
Source: https://osv.dev/vulnerability/CVE-2020-24715
Type: osv

## Details
The Scalyr Agent before 2.1.10 has Missing SSL Certificate Validation because, in some circumstances, native Python code is used that lacks a comparison of the hostname to commonName and subjectAltName.

## References
- https://scalyr-static.s3.amazonaws.com/technical-details/index.html
