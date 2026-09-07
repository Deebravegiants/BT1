# [M] Robocode Arbitrary Code Execution

## Summary
Severity: Medium
Advisory: GHSA-xh22-fw58-56pp
CVE: CVE-2007-6382
CWE: CWE-94
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-xh22-fw58-56pp
Type: github-advisory

## Affected
- Maven: `net.sf.robocode:robocode.core` — affected >=0 <1.5.1

## Details
The Event Dispatch Thread in Robocode before 1.5.1 allows remote attackers to execute arbitrary Java code by using a robot to invoke the `SwingUtilities.invokeLater` method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-6382
- https://github.com/robo-code/robocode/commit/2f2867d24fb28a2478983be57556f2355a774a81
- https://github.com/robo-code/robocode/commit/8c6f5d77e7723583ba069ea611c33f22c1e9603a
- https://exchange.xforce.ibmcloud.com/vulnerabilities/39019
- https://github.com/robo-code/robocode
- https://github.com/robo-code/robocode/blob/1abe65b65c34a8eb3d23de8f037dafae3c548fa5/versions.md?plain=1#L1880-L1887
