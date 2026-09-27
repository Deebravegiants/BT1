# [M] Axios: unbounded recursion in toFormData causes DoS via deeply nested request data

## Summary
Severity: Medium
Advisory: GHSA-62hf-57xw-28j9
CVE: CVE-2026-42039
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-62hf-57xw-28j9
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.15.1
- npm: `axios` — affected >=0 <0.31.1

## Details
### Summary
toFormData recursively walks nested objects with no depth limit, so a deeply nested value passed as request data crashes the Node.js process with a RangeError.

### Details
lib/helpers/toFormData.js:210 defines an inner `build(value, path)` that recurses into every object/array child (line 225: `build(el, path ? path.concat(key) : [key])`). The only safeguard is a `stack` array used to detect circular references; there is no maximum depth and no try/catch around the recursion. Because `build` calls itself once per nesting level, a payload nested roughly 2000+ levels deep exhausts V8's call stack.

`toFormData` is the serializer behind `FormData` request bodies and `AxiosURLSearchParams` (used by `buildURL` when `params` is an object with `URLSearchParams` unavailable, see `lib/helpers/buildURL.js:53` and `lib/helpers/AxiosURLSearchParams.js:36`). Any server-side code that forwards a client-supplied object into `axios({ data, params })` therefore reaches the recursive walker with attacker-controlled depth.

The RangeError is thrown synchronously from inside `forEach`, escapes `toFormData`, and propagates out of the axios request call. In typical Express/Fastify request handlers this terminates the running request; in synchronous startup paths or worker threads it can crash the whole process.

### PoC
```js
import toFormData from 'axios/lib/helpers/toFormData.js';
import FormData from 'form-data';

function nest(depth) {
  let o = { leaf: 1 };
  for (let i = 0; i < depth; i++) o = { a: o };
  return o;
}

try {
  toFormData(nest(2500), new FormData());
} catch (e) {
  console.log(e.name + ': ' + e.message);
}
// RangeError: Maximum call stack size exceeded
```

Server-side reachability example:
```js
// vulnerable proxy pattern
app.post('/forward', async (req, res) => {
  await axios.post('https://upstream/api', req.body); // req.body user-controlled
  res.send('ok');
});
// attacker POST /forward with {"a":{"a":{"a":... 2500 deep ...}}}
// -> toFormData build() overflows -> request handler crashes
```

Verified on axios 1.15.0 (latest, 2026-04-10), Node.js 20, 3/3 PoC runs reproduce the RangeError at depth 2500.

### Impact
A remote, unauthenticated attacker who can influence an object passed to axios as request `data` or `params` triggers an uncaught RangeError inside the synchronous recursive walker. In server-side applications that proxy or re-send client JSON through axios this crashes the request handler and, in worker/cluster setups, the process. Fix by bounding recursion depth in `toFormData`'s `build` function (reject or throw on depths beyond a configurable limit, e.g. 100) or rewriting the walker iteratively.

## References
- https://github.com/axios/axios/security/advisories/GHSA-62hf-57xw-28j9
- https://nvd.nist.gov/vuln/detail/CVE-2026-42039
- https://github.com/axios/axios/commit/85132ffba1a77609ea5d101c8a413dea7174932f
- https://github.com/axios/axios
- https://github.com/axios/axios/releases/tag/v1.15.1
