# [H] CVE-2021-21248

## Summary
Severity: High
Advisory: CVE-2021-21248
Aliases: GHSA-gwp4-5498-hv5f
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-15
Source: https://osv.dev/vulnerability/CVE-2021-21248
Type: osv

## Details
OneDev is an all-in-one devops platform. In OneDev before version 4.0.3, there is a critical vulnerability involving the build endpoint parameters. InputSpec is used to define parameters of a Build spec. It does so by using dynamically generated Groovy classes. A user able to control job parameters can run arbitrary code on OneDev's server by injecting arbitrary Groovy code. The ultimate result is in the injection of a static constructor that will run arbitrary code. For a full example refer to the referenced GHSA. This issue was addressed in 4.0.3 by escaping special characters such as quote from user input.

## References
- https://github.com/theonedev/onedev/security/advisories/GHSA-gwp4-5498-hv5f
- https://github.com/theonedev/onedev/commit/39d95ab8122c5d9ed18e69dc024870cae08d2d60
