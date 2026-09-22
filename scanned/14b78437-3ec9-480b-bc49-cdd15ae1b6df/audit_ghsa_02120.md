# [H] Path Traversal in the Java Kubernetes Client

## Summary
Severity: High
Advisory: GHSA-cghx-9gcr-r42x
CVE: CVE-2020-8570
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-01-29
Source: https://github.com/advisories/GHSA-cghx-9gcr-r42x
Type: github-advisory

## Affected
- Maven: `io.kubernetes:client-java` — affected >=0 <9.0.2
- Maven: `io.kubernetes:client-java` — affected >=10.0.0 <10.0.1

## Details
Kubernetes Java client libraries in version 10.0.0 and versions prior to 9.0.1 allow writes to paths outside of the current directory when copying multiple files from a remote pod which sends a maliciously crafted archive. This can potentially overwrite any files on the system of the process executing the client code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8570
- https://github.com/kubernetes-client/java/issues/1491
- https://github.com/kubernetes-client/java/pull/1450
- https://github.com/kubernetes-client/java/commit/858316ae8bc1145005a0310e1f65f95d2389a589
- https://github.com/kubernetes-client/java
- https://groups.google.com/g/kubernetes-security-announce/c/sd5h73sFPrg
- https://lists.apache.org/thread.html/r0c76b3d0be348f788cd947054141de0229af00c540564711e828fd40@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/r1975078e44d96f2a199aa90aa874b57a202eaf7f25f2fde6d1c44942@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/rcafa485d63550657f068775801aeb706b7a07140a8ebbdef822b3bb3@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/rdb223e1b82e3d7d8e4eaddce8dd1ab87252e3935cc41c859f49767b6@%3Ccommits.druid.apache.org%3E
