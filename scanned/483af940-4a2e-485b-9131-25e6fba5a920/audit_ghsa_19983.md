# [H] SnakeYaml Constructor Deserialization Remote Code Execution

## Summary
Severity: High
Advisory: GHSA-mjmj-j48q-9wg2
CVE: CVE-2022-1471
CWE: CWE-20, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2022-12-12
Source: https://github.com/advisories/GHSA-mjmj-j48q-9wg2
Type: github-advisory

## Affected
- Maven: `org.yaml:snakeyaml` — affected >=0 <2.0

## Details
### Summary
SnakeYaml's `Constructor` class, which inherits from `SafeConstructor`, allows
any type be deserialized given the following line:

new Yaml(new Constructor(TestDataClass.class)).load(yamlContent);

Types do not have to match the types of properties in the
target class. A `ConstructorException` is thrown, but only after a malicious
payload is deserialized.

### Severity
High, lack of type checks during deserialization allows remote code execution.

### Proof of Concept
Execute `bash run.sh`. The PoC uses Constructor to deserialize a payload
for RCE. RCE is demonstrated by using a payload which performs a http request to
http://127.0.0.1:8000.

Example output of successful run of proof of concept:

```
$ bash run.sh

[+] Downloading snakeyaml if needed
[+] Starting mock HTTP server on 127.0.0.1:8000 to demonstrate RCE
nc: no process found
[+] Compiling and running Proof of Concept, which a payload that sends a HTTP request to mock web server.
[+] An exception is expected.
Exception:
Cannot create property=payload for JavaBean=Main$TestDataClass@3cbbc1e0
 in 'string', line 1, column 1:
    payload: !!javax.script.ScriptEn ... 
    ^
Can not set java.lang.String field Main$TestDataClass.payload to javax.script.ScriptEngineManager
 in 'string', line 1, column 10:
    payload: !!javax.script.ScriptEngineManag ... 
             ^

	at org.yaml.snakeyaml.constructor.Constructor$ConstructMapping.constructJavaBean2ndStep(Constructor.java:291)
	at org.yaml.snakeyaml.constructor.Constructor$ConstructMapping.construct(Constructor.java:172)
	at org.yaml.snakeyaml.constructor.Constructor$ConstructYamlObject.construct(Constructor.java:332)
	at org.yaml.snakeyaml.constructor.BaseConstructor.constructObjectNoCheck(BaseConstructor.java:230)
	at org.yaml.snakeyaml.constructor.BaseConstructor.constructObject(BaseConstructor.java:220)
	at org.yaml.snakeyaml.constructor.BaseConstructor.constructDocument(BaseConstructor.java:174)
	at org.yaml.snakeyaml.constructor.BaseConstructor.getSingleData(BaseConstructor.java:158)
	at org.yaml.snakeyaml.Yaml.loadFromReader(Yaml.java:491)
	at org.yaml.snakeyaml.Yaml.load(Yaml.java:416)
	at Main.main(Main.java:37)
Caused by: java.lang.IllegalArgumentException: Can not set java.lang.String field Main$TestDataClass.payload to javax.script.ScriptEngineManager
	at java.base/jdk.internal.reflect.UnsafeFieldAccessorImpl.throwSetIllegalArgumentException(UnsafeFieldAccessorImpl.java:167)
	at java.base/jdk.internal.reflect.UnsafeFieldAccessorImpl.throwSetIllegalArgumentException(UnsafeFieldAccessorImpl.java:171)
	at java.base/jdk.internal.reflect.UnsafeObjectFieldAccessorImpl.set(UnsafeObjectFieldAccessorImpl.java:81)
	at java.base/java.lang.reflect.Field.set(Field.java:780)
	at org.yaml.snakeyaml.introspector.FieldProperty.set(FieldProperty.java:44)
	at org.yaml.snakeyaml.constructor.Constructor$ConstructMapping.constructJavaBean2ndStep(Constructor.java:286)
	... 9 more
[+] Dumping Received HTTP Request. Will not be empty if PoC worked
GET /proof-of-concept HTTP/1.1
User-Agent: Java/11.0.14
Host: localhost:8000
Accept: text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2
Connection: keep-alive
```

### Further Analysis
Potential mitigations include, leveraging SnakeYaml's SafeConstructor while parsing untrusted content.

See https://bitbucket.org/snakeyaml/snakeyaml/issues/561/cve-2022-1471-vulnerability-in#comment-64581479 for discussion on the subject.

### Timeline
**Date reported**: 4/11/2022
**Date fixed**:  [30/12/2022](https://bitbucket.org/snakeyaml/snakeyaml/pull-requests/44)
**Date disclosed**: 10/13/2022

## References
- https://github.com/google/security-research/security/advisories/GHSA-mjmj-j48q-9wg2
- https://nvd.nist.gov/vuln/detail/CVE-2022-1471
- https://www.github.com/mbechler/marshalsec/blob/master/marshalsec.pdf?raw=true
- https://snyk.io/blog/unsafe-deserialization-snakeyaml-java-cve-2022-1471
- https://security.netapp.com/advisory/ntap-20240621-0006
- https://security.netapp.com/advisory/ntap-20230818-0015
- https://infosecwriteups.com/%EF%B8%8F-inside-the-160-comment-fight-to-fix-snakeyamls-rce-default-1a20c5ca4d4c
- https://groups.google.com/g/kubernetes-security-announce/c/mwrakFaEdnc
- https://github.com/mbechler/marshalsec
- https://confluence.atlassian.com/security/cve-2022-1471-snakeyaml-library-rce-vulnerability-in-multiple-products-1296171009.html
- https://bitbucket.org/snakeyaml/snakeyaml/wiki/CVE-2022-1471
- https://bitbucket.org/snakeyaml/snakeyaml/issues/561/cve-2022-1471-vulnerability-in#comment-64876314
- https://bitbucket.org/snakeyaml/snakeyaml/issues/561/cve-2022-1471-vulnerability-in#comment-64634374
- https://bitbucket.org/snakeyaml/snakeyaml/issues/561/cve-2022-1471-vulnerability-in#comment-64581479
- https://bitbucket.org/snakeyaml/snakeyaml/commits/acc44099f5f4af26ff86b4e4e4cc1c874e2dc5c4
- https://bitbucket.org/snakeyaml/snakeyaml/commits/5014df1a36f50aca54405bb8433bc99a8847f758
- https://bitbucket.org/snakeyaml/snakeyaml
- http://packetstormsecurity.com/files/175095/PyTorch-Model-Server-Registration-Deserialization-Remote-Code-Execution.html
- http://www.openwall.com/lists/oss-security/2023/11/19/1
