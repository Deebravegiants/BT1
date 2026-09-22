# [M] Path Traversal and Improper Input Validation in Apache Commons IO

## Summary
Severity: Medium
Advisory: GHSA-gwrp-pvrq-jmwv
CVE: CVE-2021-29425
CWE: CWE-20, CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-04-26
Source: https://github.com/advisories/GHSA-gwrp-pvrq-jmwv
Type: github-advisory

## Affected
- Maven: `commons-io:commons-io` — affected >=0 <2.7
- Maven: `com.cosium.vet:vet` — affected >=1.0
- Maven: `com.diamondq.common:common-thirdparty.jcasbin` — affected 1.4.0
- Maven: `com.liferay:com.liferay.sass.compiler.jsass` — affected 1.0.1
- Maven: `com.virjar:ratel-api` — affected >=1.0.0
- Maven: `net.hasor:cobble-lang` — affected >=4.4.1
- Maven: `org.apache.commons:commons-io` — affected 1.3.2
- Maven: `org.apache.servicemix.bundles:org.apache.servicemix.bundles.commons-io` — affected >=1.4
- Maven: `org.checkerframework.annotatedlib:commons-io` — affected >=2.6 <2.7
- Maven: `org.smartboot.servlet:servlet-core` — affected >=0.1.9

## Details
In Apache Commons IO before 2.7, When invoking the method FileNameUtils.normalize with an improper input string, like "//../foo", or "\\..\foo", the result would be the same value, thus possibly providing access to files in the parent directory, but not further above (thus "limited" path traversal), if the calling code would use the result to construct a path value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29425
- https://lists.apache.org/thread.html/r8efcbabde973ea72f5e0933adc48ef1425db5cde850bf641b3993f31@%3Cdev.commons.apache.org%3E
- https://lists.apache.org/thread.html/r92ea904f4bae190b03bd42a4355ce3c2fbe8f36ab673e03f6ca3f9fa@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/ra8ef65aedc086d2d3d21492b4c08ae0eb8a3a42cc52e29ba1bc009d8@%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/raa053846cae9d497606027816ae87b4e002b2e0eb66cb0dee710e1f5@%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/rad4ae544747df32ccd58fff5a86cd556640396aeb161aa71dd3d192a@%3Cuser.commons.apache.org%3E
- https://lists.apache.org/thread.html/rbebd3e19651baa7a4a5503a9901c95989df9d40602c8e35cb05d3eb5@%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/rc10fa20ef4d13cbf6ebe0b06b5edb95466a1424a9b7673074ed03260@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rc2dd3204260e9227a67253ef68b6f1599446005bfa0e1ddce4573a80@%3Cpluto-dev.portals.apache.org%3E
- https://lists.apache.org/thread.html/rc359823b5500e9a9a2572678ddb8e01d3505a7ffcadfa8d13b8780ab%40%3Cuser.commons.apache.org%3E
- https://lists.apache.org/thread.html/rc5f3df5316c5237b78a3dff5ab95b311ad08e61d418cd992ca7e34ae@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rc65f9bc679feffe4589ea0981ee98bc0af9139470f077a91580eeee0@%3Cpluto-dev.portals.apache.org%3E
- https://lists.apache.org/thread.html/rca71a10ca533eb9bfac2d590533f02e6fb9064d3b6aa3ec90fdc4f51@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rd09d4ab3e32e4b3a480e2ff6ff118712981ca82e817f28f2a85652a6@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/re41e9967bee064e7369411c28f0f5b2ad28b8334907c9c6208017279@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/red3aea910403d8620c73e1c7b9c9b145798d0469eb3298a7be7891af@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rfa2f08b7c0caf80ca9f4a18bd875918fdd4e894e2ea47942a4589b9c@%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/rfcd2c649c205f12b72dde044f905903460669a220a2eb7e12652d19d@%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rfd01af05babc95b8949e6d8ea78d9834699e1b06981040dde419a330@%3Cdev.commons.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/08/msg00016.html
