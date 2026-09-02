### Title
Webhook shop identity not covered by HMAC verification allows cross-tenant shop spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats an incoming webhook as authenticated for a given shop as long as `Utils::HmacValidator.validate(request)` returns true, and then hands `request.shop` straight to the app's handler as the merchant/tenant identifier. However, the HMAC signature verified by `HmacValidator` only covers the raw request body — it never covers the `shop` value. This breaks the intended binding `verified(bytes) == shop-identity-acted-on`, letting an attacker who possesses one validly-signed webhook payload (e.g. one delivered for their own installed shop) replay it with a forged `X-Shopify-Shop-Domain`/`shopify-shop-domain` header pointing at a different merchant.

### Finding Description
`Webhooks::Request#to_signable_string` only returns the raw body: [1](#0-0) 

`Webhooks::Request#shop` is read from an HTTP header that is never part of the signed material: [2](#0-1) 

`HmacValidator.validate` computes the HMAC only over `verifiable_query.to_signable_string` (the body) and compares it against the received `hmac`: [3](#0-2) 

`Registry.process` gates entirely on this body-only HMAC check, then forwards the unauthenticated `request.shop` value to the app's handler as the trusted tenant identity: [4](#0-3) 

The identity equality that should hold is: `hmac_verified(bytes) == shop_the_app_will_act_on`. In this code path that equality is never enforced — `hmac_verified(bytes)` only proves the body came from Shopify for *some* shop, while `shop_the_app_will_act_on` (`request.shop`) is taken from an attacker-controllable header. An unprivileged internet user who can install the app on any shop (including their own) receives legitimately-signed webhook deliveries (valid HMAC over a JSON body they can freely inspect/replay, since HMAC-signed webhook POSTs are just HTTP requests to the app's public endpoint). They can then resend that same body+HMAC pair to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop that also uses the same multi-tenant app. `Utils::HmacValidator.validate` still returns `true` (body/HMAC pair is unmodified and valid), and `Registry.process` dispatches to the handler with `WebhookMetadata#shop` set to the victim's domain, while the `body` content actually belongs to the attacker's own shop. Any host application that uses `WebhookMetadata#shop` (as documented/intended by this gem) to select the tenant record to update will write or act on attacker-controlled data under the victim's tenant identity — a cross-tenant identity-binding break rooted entirely in this gem's own webhook-verification code.

### Impact Explanation
This is a cross-tenant access vulnerability: a shop the attacker does not own can be made to receive/act on webhook data that only proves authenticity for a different (attacker-controlled) shop, because the library's HMAC verification does not bind the `shop` field it exposes to callers. This satisfies the Critical cross-tenant access bar, since the trust boundary between merchants processed by the same app installation is broken using only a normal, unprivileged app-install capability (no `api_secret_key`, no access token, no privileged account needed).

### Likelihood Explanation
Any user can install the target app on a shop they control and thereby obtain at least one validly HMAC-signed webhook body/signature pair for a topic the app subscribes to. Replaying that exact body with only the `shop-domain` header changed requires no cryptographic material and no rate-limited guessing — it is a straightforward, deterministic HTTP replay against the app's already-public webhook endpoint. Likelihood is high for any app relying on `WebhookMetadata#shop` for tenant selection, which is the documented usage pattern of this library.

### Recommendation
Bind the shop (and topic/webhook id) into the value that is actually HMAC-verified, e.g. by having `Webhooks::Request#to_signable_string` incorporate the `shop`, `topic`, and `webhook_id` header values alongside the raw body (or by independently verifying the `shop` header against a shop-scoped webhook secret/session lookup) so that a body+HMAC pair valid for one shop cannot be replayed under another shop's identity. At minimum, the gem should not expose `request.shop` as trustworthy after only validating the HMAC over the body.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers an event that causes Shopify to deliver a webhook to the app, capturing the exact raw body and its `X-Shopify-Hmac-Sha256` value — this HMAC is valid because `HmacValidator` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) only signs `@raw_body` (`lib/shopify_api/webhooks/request.rb:36-38`).
3. Attacker resends the identical body and HMAC header to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` returns `true` (body unchanged) at `lib/shopify_api/webhooks/registry.rb:190`.
5. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker's body>, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`) and dispatches it to the app's handler, which acts on victim-shop's tenant record using attacker-supplied body content.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
