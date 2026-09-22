# [M] skylot jadx affected by Incorrect Behavior Order in vulnerable dependency

## Summary
Severity: Medium
Advisory: GHSA-fjh6-p566-wr6q
CWE: CWE-696
Ecosystem: Maven
Published: 2022-07-21
Source: https://github.com/advisories/GHSA-fjh6-p566-wr6q
Type: github-advisory

## Affected
- Maven: `io.github.skylot:jadx-core` — affected >=0 <1.4.3

## Details
### Impact
Vulnerable library protobuf-java 3.11.4 (CVE-2021-22569)

### Patches
Dependency updated in jadx 1.4.3

### References
According to the AquaSecurity report:
![05F1C52A666E4FCC844ABD085BD55124](https://user-images.githubusercontent.com/118523/177364939-087e2144-9a8a-4594-ae90-eb2acb0a2036.png)

Also, Maven repository have links to this and other vulnerabilities from dependencies:
https://mvnrepository.com/artifact/com.google.protobuf/protobuf-java/3.11.4

## References
- https://github.com/skylot/jadx/security/advisories/GHSA-fjh6-p566-wr6q
- https://github.com/skylot/jadx
- https://github.com/skylot/jadx/releases/tag/v1.4.3
