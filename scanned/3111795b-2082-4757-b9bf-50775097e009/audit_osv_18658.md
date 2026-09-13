# [C] CVE-2020-29601

## Summary
Severity: Critical
Advisory: CVE-2020-29601
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-08
Source: https://osv.dev/vulnerability/CVE-2020-29601
Type: osv

## Details
The official notary docker images before signer-0.6.1-1 contain a blank password for a root user. System using the notary docker container deployed by affected versions of the docker image may allow an remote attacker to achieve root access with a blank password.

## References
- https://github.com/koharin/koharin2/blob/main/CVE-2020-29601
