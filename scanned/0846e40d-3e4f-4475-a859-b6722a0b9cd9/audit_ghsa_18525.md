# [M] Juju vulnerable to sensitive log retrieval via authenticated endpoint without authorization

## Summary
Severity: Medium
Advisory: GHSA-r64v-82fh-xc63
CVE: CVE-2025-53512
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-r64v-82fh-xc63
Type: github-advisory

## Affected
- Go: `github.com/juju/juju` — affected >=0 <0.0.0-20250619024904-402ff008dcc2

## Details
### Impact
Any user with a Juju account on a controller can read debug log messages from the `/log` endpoint.
No specific permissions are required - it's just sufficient for the user to exist in the controller user database.
The log messages may contain sensitive information.

### Details

The `/log` endpoint is accessible at the following endpoints:
- `wss://<controller-ip>/log`
- `wss://<controller-ip>/model/<model-uuid>/log`

In order to connect to these endpoints, the client must pass an X-Juju-Client-Version header that matches the current version and pass credentials in a Basic Authorization header. Once connected, the service will stream log events even though the user is not authorised to view them.

To reproduce:

```
juju bootstrap
juju add-user testuser
juju change-user-password testuser
```
Run the [wscat](https://github.com/websockets/wscat) command below to
connect to `wss://<controller-ip>:17070/api`. Update the JSON payload to include the username and password that were created above.

```
wscat --no-check -c wss://contorller-ip:17070/model/modelUUID/api
{ "type": "Admin", "request": "Login", "version": 3, "params": { "client-
version": "3.6.1.0", "auth-tag": "user-testuser", "credentials": "
password" } }
```

Observe that the connection fails due to a lack of permissions.

Run the command below to connect to the log endpoint. Note that the credentials are passed in the --auth flag.

```
wscat --auth user-testuser:password -H "X-Juju-ClientVersion: 3.6.4" --no-check -c wss://<controller-ip>:17070/log
```

Observe that the logs are returned in the server’s response.

### Code

The `/log` handlers are registered here
https://github.com/juju/juju/blob/3.6/apiserver/apiserver.go#L867
https://github.com/juju/juju/blob/3.6/apiserver/apiserver.go#L980

And the only auth required is that the incoming request be for an authenticated user

https://github.com/juju/juju/blob/3.6/apiserver/apiserver.go#L713

but no specific permission checks are done.

### Workarounds
There are no workarounds.

### References
[F-01](https://drive.google.com/file/d/1pHRNiaA8LyMVJYwIyTqelsqJ9FmImDf0/view)

## References
- https://github.com/juju/juju/security/advisories/GHSA-r64v-82fh-xc63
- https://nvd.nist.gov/vuln/detail/CVE-2025-53512
- https://github.com/juju/juju/commit/402ff008dcc2cb57f4441968628637efb5c2a662
- https://github.com/juju/juju/commit/c91a1f4046956874ba77c8b398aecee3d61a2dc3
- https://github.com/juju/juju
