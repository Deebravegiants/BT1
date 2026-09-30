# [C] CVE-2020-11975

## Summary
Severity: Critical
Advisory: CVE-2020-11975
Aliases: GHSA-v6fq-q792-j46j
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-05
Source: https://osv.dev/vulnerability/CVE-2020-11975
Type: osv

## Details
Apache Unomi allows conditions to use OGNL scripting which offers the possibility to call static Java classes from the JDK that could execute code with the permission level of the running Java process.

## References
- https://lists.apache.org/thread.html/r01021bc4b25c1e98812efca0b07f0e078a6281bd52f7c3817a429d95%40%3Ccommits.unomi.apache.org%3E
- https://lists.apache.org/thread.html/r79672c25e0ef9bb4b9148376281200a8e61c6d5ef5bb705e9a363460%40%3Ccommits.unomi.apache.org%3E
- http://unomi.apache.org/security/cve-2020-11975.txt
