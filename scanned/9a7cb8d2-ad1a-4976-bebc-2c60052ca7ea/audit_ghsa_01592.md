# [M] TemporaryFolder on unix-like systems does not limit access to created files

## Summary
Severity: Medium
Advisory: GHSA-269g-pwp5-87pp
CVE: CVE-2020-15250
CWE: CWE-200, CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-10-12
Source: https://github.com/advisories/GHSA-269g-pwp5-87pp
Type: github-advisory

## Affected
- Maven: `junit:junit` — affected >=4.7 <4.13.1

## Details
### Vulnerability

The JUnit4 test rule [TemporaryFolder](https://junit.org/junit4/javadoc/4.13/org/junit/rules/TemporaryFolder.html) contains a local information disclosure vulnerability.

Example of vulnerable code:
```java
public static class HasTempFolder {
    @Rule
    public TemporaryFolder folder = new TemporaryFolder();

    @Test
    public void testUsingTempFolder() throws IOException {
        folder.getRoot(); // Previous file permissions: `drwxr-xr-x`; After fix:`drwx------`
        File createdFile= folder.newFile("myfile.txt"); // unchanged/irrelevant file permissions
        File createdFolder= folder.newFolder("subfolder"); // unchanged/irrelevant file permissions
        // ...
    }
}
```

### Impact

On Unix like systems, the system's temporary directory is shared between all users on that system. Because of this, when files and directories are written into this directory they are, by default, readable by other users on that same system.

This vulnerability **does not** allow other users to overwrite the contents of these directories or files. This is purely an information disclosure vulnerability.

When analyzing the impact of this vulnerability, here are the important questions to ask:

1. Do the JUnit tests write sensitive information, like API keys or passwords, into the temporary folder?
    - If yes, this vulnerability impacts you, but only if you also answer 'yes' to question 2.
    - If no, this vulnerability does not impact you.
2. Do the JUnit tests ever execute in an environment where the OS has other untrusted users. 
    _This may apply in CI/CD environments but normally won't be 'yes' for personal developer machines._
    - If yes, and you answered 'yes' to question 1, this vulnerability impacts you.
    - If no, this vulnerability does not impact you.

### Patches

Because certain JDK file system APIs were only added in JDK 1.7, this this fix is dependent upon the version of the JDK you are using.
 - Java 1.7 and higher users: this vulnerability is fixed in 4.13.1.
 - Java 1.6 and lower users: **no patch is available, you must use the workaround below.**

### Workarounds

If you are unable to patch, or are stuck running on Java 1.6, specifying the `java.io.tmpdir` system environment variable to a directory that is exclusively owned by the executing user will fix this vulnerability.

### References
- [CWE-200: Exposure of Sensitive Information to an Unauthorized Actor](https://cwe.mitre.org/data/definitions/200.html)
- Fix commit https://github.com/junit-team/junit4/commit/610155b8c22138329f0723eec22521627dbc52ae

#### Similar Vulnerabilities
 - Google Guava - https://github.com/google/guava/issues/4011
 - Apache Ant - https://nvd.nist.gov/vuln/detail/CVE-2020-1945
 - JetBrains Kotlin Compiler - https://nvd.nist.gov/vuln/detail/CVE-2020-15824

### For more information
If you have any questions or comments about this advisory, please pen an issue in [junit-team/junit4](https://github.com/junit-team/junit4/issues).

## References
- https://github.com/junit-team/junit4/security/advisories/GHSA-269g-pwp5-87pp
- https://nvd.nist.gov/vuln/detail/CVE-2020-15250
- https://github.com/junit-team/junit4/issues/1676
- https://github.com/junit-team/junit4/commit/610155b8c22138329f0723eec22521627dbc52ae
- https://lists.apache.org/thread.html/ra1bdb9efae84794e8ffa2f8474be8290ba57830eefe9714b95da714b@%3Cdev.pdfbox.apache.org%3E
- https://lists.apache.org/thread.html/raebf13f53cd5d23d990712e3d11c80da9a7bae94a6284050f148ed99@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rb2771949c676ca984e58a5cd5ca79c2634dee1945e0406e48e0f8457@%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/rb2ffe2993f4dccc48d832e1a0f1c419477781b6ea16e725ca2276dbb@%3Cdev.knox.apache.org%3E
- https://lists.apache.org/thread.html/rb33212dab7beccaf1ffef9b88610047c644f644c7a0ebdc44d77e381@%3Ccommits.turbine.apache.org%3E
- https://lists.apache.org/thread.html/rbaec90e699bc7c7bd9a053f76707a36fda48b6d558f31dc79147dbf9@%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/rc49cf1547ef6cac1be4b3c92339b2cae0acacf5acaba13cfa429a872@%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/rdbdd30510a7c4d0908fd22075c02b75bbc2e0d977ec22249ef3133cb@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rde385b8b53ed046600ef68dd6b4528dea7566aaddb02c3e702cc28bc@%3Ccommits.creadur.apache.org%3E
- https://lists.apache.org/thread.html/rde8e70b95c992378e8570e4df400c6008a9839eabdfb8f800a3e5af6@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rdef7d1380c86e7c0edf8a0f89a2a8db86fce5e363457d56b722691b4@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rea812d8612fdc46842a2a57248cad4b01ddfdb1e9b037c49e68fdbfb@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/reb700e60b9642eafa4b7922bfee80796394135aa09c7a239ef9f7486@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rf2ec93f4ca9a97d1958eb4a31b1830f723419ce9bf2018a6e5741d5b@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rf6e5d894d4b03bef537c9d6641272e0197c047c0d1982b4e176d0353@%3Cdev.knox.apache.org%3E
- https://lists.apache.org/thread.html/rf797d119cc3f51a8d7c3c5cbe50cb4524c8487282b986edde83a9467@%3Ccommits.pulsar.apache.org%3E
