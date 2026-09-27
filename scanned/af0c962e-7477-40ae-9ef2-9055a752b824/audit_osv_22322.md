# [H] CVE-2022-25181

## Summary
Severity: High
Advisory: CVE-2022-25181
Aliases: GHSA-7w2w-fwpf-9m4h
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-15
Source: https://osv.dev/vulnerability/CVE-2022-25181
Type: osv

## Details
A sandbox bypass vulnerability in Jenkins Pipeline: Shared Groovy Libraries Plugin 552.vd9cc05b8a2e1 and earlier allows attackers with Item/Configure permission to execute arbitrary code in the context of the Jenkins controller JVM through crafted SCM contents, if a global Pipeline library already exists.

## References
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2441
