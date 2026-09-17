# [H] Improper Limitation of a Pathname to a Restricted Directory in Fabric8 Kubernetes Client

## Summary
Severity: High
Advisory: GHSA-jwh2-ffg4-48xc
CVE: CVE-2021-20218
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jwh2-ffg4-48xc
Type: github-advisory

## Affected
- Maven: `io.fabric8:kubernetes-client` — affected >=4.2.0 <4.7.2
- Maven: `io.fabric8:kubernetes-client` — affected >=4.8.0 <4.11.2
- Maven: `io.fabric8:kubernetes-client` — affected >=4.12.0 <4.13.2
- Maven: `io.fabric8:kubernetes-client` — affected >=5.0.0 <5.0.2

## Details
A flaw was found in the fabric8 kubernetes-client in version 4.2.0 and after. This flaw allows a malicious pod/container to cause applications using the fabric8 kubernetes-client `copy` command to extract files outside the working path. The highest threat from this vulnerability is to integrity and system availability. This has been fixed in kubernetes-client-4.13.2 kubernetes-client-5.0.2 kubernetes-client-4.11.2 kubernetes-client-4.7.2

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20218
- https://github.com/fabric8io/kubernetes-client/issues/2715
- https://bugzilla.redhat.com/show_bug.cgi?id=1923405
