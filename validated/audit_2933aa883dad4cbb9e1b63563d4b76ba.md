## Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (`File: lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) used by webhook handlers from an HTTP header (`shopify-shop-domain`), but the HMAC signature that authenticates the webhook only covers the raw request body. Anyone who can obtain one legitimately-signed webhook (e.g. by installing the target app on their own shop, which is an unprivileged action) can replay that exact body+HMAC pair to the app's shared webhook endpoint while substituting a different `shopify-shop-domain` header, and the signature will still validate. This lets an attacker impersonate another shop to the app's webhook processing pipeline — a cross-tenant identity break analogous to the reported veNFT bug where the field actually acted upon (`staking.balanceOf`) was decoupled from the object whose ownership was actually checked.

### Finding Description
The identity binding that should hold is:

`shop header trusted by handler == shop that produced/authorized the signed bytes`

In `lib/shopify_api/webhooks/request.rb`:
```
def shop
  T.cast(shopify_header("shop-domain"), String)
end
...
def to_signable_string
  @raw_body
end
``` [1](#0-0) [2](#0-1) 

`shop` is read straight from an attacker-controllable header (`shopify-shop-domain` / `x-shopify-shop-domain`), while `to_signable_string` — the only material fed into the HMAC check — is exclusively `@raw_body`. Neither `topic`, `shop`, `api_version`, nor `webhook_id` participate in the signature.

Validation is performed generically via `Utils::HmacValidator.validate`, which computes `HMAC(api_secret_key, to_signable_string)` and compares it to the `hmac-sha256` header:
```
def validate_signature(verifiable_query, secret)
  received_signature = verifiable_query.hmac
  computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
  OpenSSL.secure_compare(computed_signature, T.must(received_signature))
end
``` [3](#0-2) 

`Registry.process` trusts this result and forwards `request.shop` straight to the app's handler as the tenant identifier:
```
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [4](#0-3) 

Crucially, `Context.api_secret_key` is a single, app-wide secret shared across every shop that installs the app — it is not per-shop. So the same HMAC key that authenticates shop A's webhook body also authenticates shop B's. Since the shop identity is outside the signed bytes, the HMAC check equality `computed_signature == received_signature` remains true even when the `shop` header is swapped for a different, unrelated shop.

### Impact Explanation
An attacker who installs the target app on their own store (an ordinary, unprivileged action requiring no credentials belonging to the victim) can capture one genuine `(raw_body, hmac-sha256)` pair delivered to their own webhook endpoint, then replay it against the app's shared webhook-processing endpoint with a forged `shopify-shop-domain` header naming a victim shop. `HmacValidator.validate` still returns `true` (same app secret, same body bytes), and `Registry.process` hands the handler `WebhookMetadata` claiming the event belongs to the victim shop. Any app logic that trusts `data.shop` to select the tenant record to update (a common and encouraged pattern per the gem's own docs) can be tricked into writing/replaying attacker-controlled data under another merchant's identity — a cross-tenant access/data-integrity break.

### Likelihood Explanation
Requires only: (1) ability to install the app once on an attacker-owned shop (free/unprivileged), (2) ability to capture and replay one webhook payload to the app's own endpoint with a modified header — no `api_secret_key`, access token, or victim credentials are needed. This is squarely within the gem's own webhook-verification code path, not a host-application misuse issue, since the gem itself defines the trust boundary that omits `shop` from the signed content.

### Recommendation
Include the shop-identifying header(s) (and ideally `topic`/`api_version`) in the signable content used for HMAC verification, or otherwise cryptographically bind the claimed `shop` to the signed payload before exposing it to handlers via `WebhookMetadata`. At minimum, document that `data.shop` is not authenticated by the HMAC and must not be used as the sole tenant selector without additional verification (e.g., cross-checking against a shop known to have an active session/webhook registration).

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, triggering a legitimate webhook delivery to the app's shared `/webhooks` endpoint with headers:
   `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over raw body>`, and some `raw_body`.
2. Attacker captures `raw_body` and `hmac-sha256` value (their own inbound traffic, not TLS interception of anyone else).
3. Attacker resends an HTTP request to the same webhook endpoint with the identical `raw_body` and `hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `raw_body`; `HmacValidator.validate` recomputes the same HMAC (same app secret, same body) and it matches — validation passes.
5. `Registry.process` calls the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker-chosen JSON>, ...)`, so the app processes attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
