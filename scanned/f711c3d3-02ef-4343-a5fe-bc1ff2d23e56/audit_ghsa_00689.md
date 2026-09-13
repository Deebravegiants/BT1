# [M] Denial of Service in Google Guava

## Summary
Severity: Medium
Advisory: GHSA-mvr2-9pj6-7w5j
CVE: CVE-2018-10237
CWE: CWE-502, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-06-15
Source: https://github.com/advisories/GHSA-mvr2-9pj6-7w5j
Type: github-advisory

## Affected
- Maven: `com.google.guava:guava` — affected >=11.0 <24.1.1-android
- Maven: `com.google.guava:guava-jdk5` — affected >=0
- Maven: `com.googlecode.guava-osgi:guava-osgi` — affected >=0
- Maven: `de.mhus.ports:vaadin-shared-deps` — affected >=0
- Maven: `org.hudsonci.lib.guava:guava` — affected >=0
- Maven: `org.sonatype.sisu:sisu-guava` — affected 0.11.1

## Details
Unbounded memory allocation in Google Guava 11.0 through 24.x before 24.1.1 allows remote attackers to conduct denial of service attacks against servers that depend on this library and deserialize attacker-provided data, because the AtomicDoubleArray class (when serialized with Java serialization) and the CompoundOrdering class (when serialized with GWT serialization) perform eager allocation without appropriate checks on what a client has sent and whether the data size is reasonable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-10237
- https://access.redhat.com/errata/RHSA-2018:2423
- https://lists.apache.org/thread.html/r223bc776a077d0795786c38cbc6e7dd808fce1a9161b00ba9c0a5d55@%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r22c8173b804cd4a420c43064ba4e363d0022aa421008b1989f7354d4@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/r27eb79a87a760335226dbfa6a7b7bffea539a535f8e80c41e482106d@%3Cdev.cxf.apache.org%3E
- https://lists.apache.org/thread.html/r2ea4e5e5aa8ad73b001a466c582899620961f47d77a40af712c1fdf9@%3Cdev.cxf.apache.org%3E
- https://lists.apache.org/thread.html/r30e7d7b6bfa630dacc41649a0e96dad75165d50474c1241068aa0f94@%3Cissues.storm.apache.org%3E
- https://lists.apache.org/thread.html/r352e40ca9874d1beb4ad95403792adca7eb295e6bc3bd7b65fabcc21@%3Ccommits.samza.apache.org%3E
- https://lists.apache.org/thread.html/r38e2ab87528d3c904e7fac496e8fd766b9277656ff95b97d6b6b6dcd@%3Cdev.cxf.apache.org%3E
- https://lists.apache.org/thread.html/r3c3b33ee5bef0c67391d27a97cbfd89d44f328cf072b601b58d4e748@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/r43491b25b2e5c368c34b106a82eff910a5cea3e90de82ad75cc16540@%3Cdev.syncope.apache.org%3E
- https://lists.apache.org/thread.html/r50fc0bcc734dd82e691d36d209258683141bfc0083739a77e56ad92d@%3Cdev.flink.apache.org%3E
- https://lists.apache.org/thread.html/r841c5e14e1b55281523ebcde661ece00b38a0569e00ef5e12bd5f6ba@%3Cissues.maven.apache.org%3E
- https://lists.apache.org/thread.html/r95799427b335807a4c54776908125c3e66597b65845ae50096d9278a@%3Cdev.cxf.apache.org%3E
- https://lists.apache.org/thread.html/ra0adb9653c7de9539b93cc8434143b655f753b9f60580ff260becb2b@%3Cusers.kafka.apache.org%3E
- https://lists.apache.org/thread.html/ra4f44016926dcb034b3b230280a18102062f94ae55b8a31bb92fed84@%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/ra8906723927aef2a599398c238eacfc845b74d812e0093ec2fc70a7d@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/rb3da574c34bc6bd37972d2266af3093b90d7e437460423c24f477919@%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/rc78f6e84f82cc662860e96526d8ab969f34dbe12dc560e22d9d147a3@%3Cdev.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rc8467f357b943ceaa86f289f8bc1a5d1c7955b75d3bac1426f2d4ac1@%3Ccommon-dev.hadoop.apache.org%3E
