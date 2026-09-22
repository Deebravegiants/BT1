# [C] HydrAIDE Authentication Bypass Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-qp7j-x725-g67f
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-19
Source: https://github.com/advisories/GHSA-qp7j-x725-g67f
Type: github-advisory

## Affected
- Go: `github.com/hydraide/hydraide` — affected >=2.1.1 <2.2.1
- Go: `github.com/hydraide/hydraide` — affected >=0 <0.0.0-20250816184905-1256db38c33c

## Details
### Summary
There is no authentication of any kind.


### Details
TLS is implemented, the tunnel between the client and server is secure, however once data is on the server, it's free to be read by any adversaries.

On the client side : https://github.com/hydraide/hydraide/blob/main/sdk/go/hydraidego/client/client.go#L221
It should be using a TLS Config with RootCAs and Certificates, currently RootCAs only (under NewClientTLSFromFile)

And on the server side, there should be ClientCAs and ClientAuth filled.

### PoC
To bypass as is, the simplest way is to take the client and modify the code as such : 

Modified from https://github.com/hydraide/hydraide/blob/main/sdk/go/hydraidego/client/client.go#L209
```go
			// hostOnly := strings.Split(server.Host, ":")[0]
			// creds, certErr := credentials.NewClientTLSFromFile(server.CertFilePath, hostOnly)
			// if certErr != nil {
			// 	slog.Error("error while loading TLS credentials: ", "error", certErr, "server", server.Host, "fromIsland", server.FromIsland, "toIsland", server.ToIsland)
			// 	errorMessages = append(errorMessages, certErr)
			// }
			var opts []grpc.DialOption
			tlsConfig := &tls.Config{
				InsecureSkipVerify: true,
			}
			creds := credentials.NewTLS(tlsConfig)
			opts = append(opts, grpc.WithTransportCredentials(creds))
```

### Impact
It impacts everyone who think there is any kind of authentication.

---

## Resolution

This vulnerability has been fully fixed in server/v2.2.1 together with hydraidectl/v0.2.1.

All users are strongly advised to upgrade:

1. Update to hydraidectl v0.2.1
2. Re-initialize server instances with hydraidectl init into a new folder. This generates the required certificate files, downloads the latest binaries, and sets up the necessary environment variables.

For migration help, join the community Discord: https://discord.gg/xE2YSkzFRm or open a GitHub Discussion.
If anything does not work, please report it.

## References
- https://github.com/hydraide/hydraide/security/advisories/GHSA-qp7j-x725-g67f
- https://github.com/hydraide/hydraide/commit/b252554a811400a81951dc9f959b99077f187975#diff-63efbc8179fff403eb5cc642407b33c0fb21aea2c84baaf5e5223f76f5d75f55
- https://github.com/hydraide/hydraide
- https://pkg.go.dev/vuln/GO-2025-3895
