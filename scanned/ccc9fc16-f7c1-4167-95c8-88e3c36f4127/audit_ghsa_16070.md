# [M] Orchid Platform has Method Exposure Vulnerability in Modals

## Summary
Severity: Medium
Advisory: GHSA-cm46-gqf4-mv4f
CVE: CVE-2024-51992
CWE: CWE-749
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-11-12
Source: https://github.com/advisories/GHSA-cm46-gqf4-mv4f
Type: github-advisory

## Affected
- Packagist: `orchid/platform` — affected >=8.0 <14.43.0

## Details
### Impact
This vulnerability is a method exposure issue (CWE-749: Exposed Dangerous Method or Function) in the Orchid Platform’s asynchronous modal functionality, affecting users of Orchid Platform version 8 through 14.42.x. Attackers could exploit this vulnerability to call arbitrary methods within the `Screen` class, leading to potential brute force of database tables, validation checks against user credentials, and disclosure of the server’s real IP address.

### Patches
The issue has been patched in the latest release, version 14.43.0, released on November 6, 2024. Users should upgrade to version 14.43.0 or later to address this vulnerability.

### Workarounds
If upgrading to version 14.43.0 is not immediately possible, you can mitigate the vulnerability by implementing middleware to intercept and validate requests to asynchronous modal endpoints, allowing only approved methods and parameters.


Example middleware:

```php
namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class PreventBruteForceOnAsyncRoute
{
    /**
     * Methods that are restricted from being invoked via the async route.
     */
    protected array $restrictedMethods = [
        'validate',
        'handle',
        '__invoke',
        'validateWith',
        'validateWithBag',
        'callAction',
    ];

    /**
     * Handle an incoming request.
     */
    public function handle(Request $request, Closure $next): Response
    {
        // Retrieve the current route from the request.
        /** @var \Illuminate\Routing\Route|null $route */
        $route = $request->route();

        // Allow requests to routes other than "platform.async".
        if ($route?->getName() !== 'platform.async') {
            return $next($request);
        }

        // Block requests attempting to invoke any of the restricted methods.
        if (in_array($route->parameter('method'), $this->restrictedMethods)) {
            abort(503, sprintf(
                'Access to the "%s" method is restricted.',
                $route->parameter('method')
            ));
        }

        // Continue request processing for other cases.
        return $next($request);
    }
}
```

### References
- [CWE-749: Exposed Dangerous Method or Function](https://cwe.mitre.org/data/definitions/749.html)

### Acknowledgements

We would like to extend our sincere gratitude to **Positive Technologies** and researcher **Vladislav Gladky** for identifying the vulnerability and their significant contribution to enhancing the security of our platform. Their expertise and dedication play a crucial role in making **Orchid** more reliable and secure for all users.

## References
- https://github.com/orchidsoftware/platform/security/advisories/GHSA-cm46-gqf4-mv4f
- https://nvd.nist.gov/vuln/detail/CVE-2024-51992
- https://github.com/orchidsoftware/platform
