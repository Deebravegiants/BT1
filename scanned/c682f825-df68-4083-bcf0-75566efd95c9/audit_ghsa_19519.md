# [M] pnpm uses the md5 path shortening function causes packet paths to coincide, which causes indirect packet overwriting

## Summary
Severity: Medium
Advisory: GHSA-8cc4-rfj6-fhg4
CVE: CVE-2024-47829
CWE: CWE-328
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2025-04-23
Source: https://github.com/advisories/GHSA-8cc4-rfj6-fhg4
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=0 <10.0.0

## Details
The path shortening function is used in pnpm：
```
export function depPathToFilename (depPath: string, maxLengthWithoutHash: number): string {
  let filename = depPathToFilenameUnescaped(depPath).replace(/[\\/:*?"<>|]/g, '+')
  if (filename.includes('(')) {
    filename = filename
      .replace(/\)$/, '')
      .replace(/(\)\()|\(|\)/g, '_')
  }
  if (filename.length > maxLengthWithoutHash || filename !== filename.toLowerCase() && !filename.startsWith('file+')) {
    return `${filename.substring(0, maxLengthWithoutHash - 27)}_${createBase32Hash(filename)}`
  }
  return filename
}
```
However, it uses the md5 function as a path shortening compression function, and if a collision occurs, it will result in the same storage path for two different libraries. Although the real names are under the package name /node_modoules/, there are no version numbers for the libraries they refer to.
![Schematic picture](https://github.com/user-attachments/assets/7b8b87ab-f297-47bd-a9dd-43be86e36ed2)
In the diagram, we assume that two packages are called packageA and packageB, and that the first 90 digits of their package names must be the same, and that the hash value of the package names with versions must be the same.  Then C is the package that they both reference, but with a different version number.  (npm allows package names up to 214 bytes, so constructing such a collision package name is obvious.)

Then hash(packageA@1.2.3)=hash(packageB@3.4.5).  This results in the same path for the installation, and thus under the same directory.  Although the package names under node_modoules are the full paths again, they are shared with C.
What is the exact version number of C?
In our local tests, it depends on which one is installed later.  If packageB is installed later, the C version number will change to 2.0.0.  At this time, although package A requires the C@1.0.0 version, package. json will only work during installation, and will not affect the actual operation.
We did not receive any installation error issues from pnpm during our local testing, nor did we use force, which is clearly a case that can be triggered.

For a package with a package name + version number longer than 120, another package can be constructed to introduce an indirect reference to a lower version, such as one with some known vulnerability.
Alternatively, it is possible to construct two packages with more than 120 package names + version numbers.
This is clearly an advantage for those intent on carrying out supply chain attacks.


The solution:
The repair cost is also very low, just need to upgrade the md5 function to sha256.

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-8cc4-rfj6-fhg4
- https://nvd.nist.gov/vuln/detail/CVE-2024-47829
- https://github.com/pnpm/pnpm
