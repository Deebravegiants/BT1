# [H] Improper Handling of Length Parameter Inconsistency in Compress

## Summary
Severity: High
Advisory: GHSA-mc84-pj99-q6hh
CVE: CVE-2021-36090
CWE: CWE-130
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-02
Source: https://github.com/advisories/GHSA-mc84-pj99-q6hh
Type: github-advisory

## Affected
- Maven: `org.apache.commons:commons-compress` — affected >=0 <1.21

## Details
When reading a specially crafted ZIP archive, Compress can be made to allocate large amounts of memory that finally leads to an out of memory error even for very small inputs. This could be used to mount a denial of service attack against services that use Compress' zip package.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36090
- https://commons.apache.org/proper/commons-compress/security-reports.html
- https://lists.apache.org/thread.html/rbbf42642c3e4167788a7c13763d192ee049604d099681f765385d99d@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/rbe91c512c5385181149ab087b6c909825d34299f5c491c6482a2ed57@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/rc4134026d7d7b053d4f9f2205531122732405012c8804fd850a9b26f%40%3Cuser.commons.apache.org%3E
- https://lists.apache.org/thread.html/rc7df4c2f0bbe2028a1498a46d322c91184f7a369e3e4c57d9518cacf@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/rd4332baaf6debd03d60deb7ec93bee49e5fdbe958cb6800dff7fb00e@%3Cnotifications.skywalking.apache.org%3E
- https://lists.apache.org/thread.html/rdd5412a5b9a25aed2a02c3317052d38a97128314d50bc1ed36e81d38@%3Cuser.ant.apache.org%3E
- https://lists.apache.org/thread.html/rf2f4d7940371a7c7c5b679f50e28fc7fcc82cd00670ced87e013ac88@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/rf3f0a09fee197168a813966c5816157f6c600a47313a0d6813148ea6@%3Cissues.drill.apache.org%3E
- https://lists.apache.org/thread.html/rf93b6bb267580e01deb7f3696f7eaca00a290c66189a658cf7230a1a@%3Cissues.drill.apache.org%3E
- https://lists.apache.org/thread.html/rfba19167efc785ad3561e7ef29f340d65ac8f0d897aed00e0731e742@%3Cnotifications.skywalking.apache.org%3E
- https://security.netapp.com/advisory/ntap-20211022-0001
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://lists.apache.org/thread.html/r0e87177f8e78b4ee453cd4d3d8f4ddec6f10d2c27707dd71e12cafc9@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r25f4c44616045085bc3cf901bb7e68e445eee53d1966fc08998fc456@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/r3227b1287e5bd8db6523b862c22676b046ad8f4fc96433225f46a2bd@%3Cissues.drill.apache.org%3E
