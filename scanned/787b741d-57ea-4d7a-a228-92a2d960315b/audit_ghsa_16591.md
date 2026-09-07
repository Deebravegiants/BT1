# [M] Denial of service of Minder Server with attacker-controlled REST endpoint

## Summary
Severity: Medium
Advisory: GHSA-fjw8-3gp8-4cvx
CVE: CVE-2024-35185
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-05-16
Source: https://github.com/advisories/GHSA-fjw8-3gp8-4cvx
Type: github-advisory

## Affected
- Go: `github.com/stacklok/minder` — affected >=0 <0.0.49

## Details
The Minder REST ingester is vulnerable to a denial of service attack via an attacker-controlled REST endpoint that can crash the Minder server.

The REST ingester allows users to interact with REST endpoints to fetch data for rule evaluation. When fetching data with the REST ingester, Minder sends a request to an endpoint and will use the data from the body of the response as the data to evaluate against a certain rule. Minder sends the request on these lines:
https://github.com/stacklok/minder/blob/daccbc12e364e2d407d56b87a13f7bb24cbdb074/internal/engine/ingester/rest/rest.go#L131-L139

… and parses the response body on these lines:

https://github.com/stacklok/minder/blob/daccbc12e364e2d407d56b87a13f7bb24cbdb074/internal/engine/ingester/rest/rest.go#L147-L150

https://github.com/stacklok/minder/blob/daccbc12e364e2d407d56b87a13f7bb24cbdb074/internal/engine/ingester/rest/rest.go#L196-L220

Minder creates the URL of the endpoint via templating on these lines:

https://github.com/stacklok/minder/blob/daccbc12e364e2d407d56b87a13f7bb24cbdb074/internal/engine/ingester/rest/rest.go#L121-L123

As far as I can tell, at this stage in rule evaluation, users fully control the raw template and the params passed to the template via the RuleType type:

https://github.com/stacklok/minder/blob/daccbc12e364e2d407d56b87a13f7bb24cbdb074/pkg/api/protobuf/go/minder/v1/minder.pb.go#L6151-L6173

I have not seen anything that enforces users to only send requests to GitHub REST endpoints. If there is such a constraint, it limits the ease with which this vulnerability can be exploited, but it is still possible. If there is not such a constraint, it is easy to exploit this vuln.

When Minder parses the response from a remote endpoint, it reads the response entirely into memory on these lines:

https://github.com/stacklok/minder/blob/daccbc12e364e2d407d56b87a13f7bb24cbdb074/internal/engine/ingester/rest/rest.go#L207

and

https://github.com/stacklok/minder/blob/daccbc12e364e2d407d56b87a13f7bb24cbdb074/internal/engine/ingester/rest/rest.go#L213

If the response is sufficiently large, it can drain memory on the machine and crash the Minder server.

The attacker can control the remote REST endpoints that Minder sends requests to, and they can configure the remote REST endpoints to return responses with large bodies.  They would then instruct Minder to send a request to their configured endpoint that would return the large response which would crash the Minder server.

## References
- https://github.com/stacklok/minder/security/advisories/GHSA-fjw8-3gp8-4cvx
- https://nvd.nist.gov/vuln/detail/CVE-2024-35185
- https://github.com/stacklok/minder/commit/065049336aac0621ee00a0bb2211f8051d47c14b
- https://github.com/stacklok/minder
