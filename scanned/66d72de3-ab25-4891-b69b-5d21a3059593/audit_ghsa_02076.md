# [C] Origin Validation Error in Apache Maven

## Summary
Severity: Critical
Advisory: GHSA-2f88-5hg8-9x2x
CVE: CVE-2021-26291
CWE: CWE-346
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-2f88-5hg8-9x2x
Type: github-advisory

## Affected
- Maven: `org.apache.maven:maven-compat` — affected >=0 <3.8.1
- Maven: `org.apache.maven:maven-core` — affected >=0 <3.8.1

## Details
Apache Maven will follow repositories that are defined in a dependency’s Project Object Model (pom) which may be surprising to some users, resulting in potential risk if a malicious actor takes over that repository or is able to insert themselves into a position to pretend to be that repository. Maven is changing the default behavior in 3.8.1+ to no longer follow http (non-SSL) repository references by default. More details available in the referenced urls. If you are currently using a repository manager to govern the repositories used by your builds, you are unaffected by the risks present in the legacy behavior, and are unaffected by this vulnerability and change to default behavior. See this link for more information about repository management: https://maven.apache.org/repository-management.html

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26291
- https://github.com/apache/maven/commit/899465aeec03753ea91e15a79579eab76369c016
- https://github.com/apache/maven/commit/fa79cb22e456cc65522b5bab8c4240fe08c5775f
- https://lists.apache.org/thread.html/r77af3ac7c3bfbd5454546e13faf7aec21d627bdcf36c9ca240436b94@%3Cissues.karaf.apache.org%3E
- https://lists.apache.org/thread.html/r78fb6d2cf0ca332cfa43abd4471e75fa6c517ed9cdfcb950bff48d40@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r86aebd0387ae19b740b3eb28bad83fe6aceca0d6257eaa810a6e0002@%3Ccommits.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r86e1c81e03f441855f127980e9b3d41939d04a7caea2b7ab718e2288@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r96cc126d3ee9aa42af9d3bb4baa94828b0a5f656584a50dcc594125f@%3Cissues.karaf.apache.org%3E
- https://lists.apache.org/thread.html/r9a027668558264c4897633e66bcb7784099fdec9f9b22c38c2442f00%40%3Cusers.maven.apache.org%3E
- https://lists.apache.org/thread.html/r9a027668558264c4897633e66bcb7784099fdec9f9b22c38c2442f00@%3Cusers.maven.apache.org%3E
- https://lists.apache.org/thread.html/ra88a0eba7f84658cefcecc0143fd8bbad52c229ee5dfcbfdde7b6457@%3Cdev.jena.apache.org%3E
- https://lists.apache.org/thread.html/ra9d984eccfd2ae7726671e025f0296bf03786e5cdf872138110ac29b@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/rc7ae2530063d1cd1cf8e9fa130d10940760f927168d4063d23b8cd0a@%3Ccommits.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rc9e441c1576bdc4375d32526d5cf457226928e9c87b9f54ded26271c@%3Cissues.karaf.apache.org%3E
- https://lists.apache.org/thread.html/rcd37d9214b08067a2e8f2b5b4fd123a1f8cb6008698d11ef44028c21@%3Cissues.karaf.apache.org%3E
- https://lists.apache.org/thread.html/rcd6c3a36f1dbc130da1b89d0f320db7040de71661a512695a8d513ac@%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rdcbad6d8ce72c79827ed8c635f9a62dd919bb21c94a0b64cab2efc31@%3Cissues.karaf.apache.org%3E
- https://lists.apache.org/thread.html/re75f8b3dbc5faa1640908f87e644d373e00f8b4e6ba3e2ba4bd2c80b@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/red3bf6cbfd99e36b0c0a4fa1cea1eef1eb300c6bd8f372f497341265@%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rf9abfc0223747a56694825c050cc6b66627a293a32ea926b3de22402@%3Cissues.karaf.apache.org%3E
