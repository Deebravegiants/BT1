Based on the in-scope library code, I found a solid identity-binding gap in the webhook verification path.

### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating that the HMAC on the raw body matches the app's secret, then dispatches the handler using the `shop` value taken from an HTTP header that is never part of the signed material. The equality the code implicitly assumes — "HMAC-verified request" == "trustworthy shop identity" — does not hold, because the signature binds only the body bytes, not the tenant (`shop`) the event is attributed to.

### Finding Description
`Utils::HmacValidator.validate` computes and compares an HMAC over `verifiable_query.to_signable_string`. For webhooks, `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` (and `topic`, `webhook_id`, `api_version`) values are read directly from HTTP headers, which are not part of the signed string at all: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity passed to the handler: [3](#0-2) 

The binding broken is: `shop verified by HMAC` (∅, since `shop` is outside `to_signable_string`) ≠ `shop used to construct WebhookMetadata` (`request.shop`, from an attacker-controllable header). Because the signature only proves "this body was HMAC'd with our secret at some point for some shop," an attacker who can obtain one legitimately-signed webhook body (e.g., by triggering any event on a store they control, or replaying a previously observed webhook whose body content is generic/reusable) can resend that exact body to the app's shared webhook endpoint while swapping the `x-shopify-shop-domain` / `shopify-shop-domain` header to a victim shop. `Utils::HmacValidator.validate(request)` still passes because it only checks the untouched raw body against the secret; the forged `shop` header sails through unchecked into the handler.

### Impact Explanation
Any host application that uses the `shop` value from `WebhookMetadata` to select which merchant's session/access token to act on, update per-shop state, or make Admin API calls, can be made to associate an attacker-controlled event body with a victim shop identity — a cross-tenant identity confusion inside a gem-provided, documented API surface (`Webhooks::Registry.process`). This matches the Critical "cross-tenant access" category, since the trust boundary between tenants is defined and enforced by this gem's `HmacValidator`/`Registry.process`, not by application code that the gem's docs tell developers to bypass.

### Likelihood Explanation
Exploitation only requires the ability to submit an HTTP request to the app's public webhook endpoint (an unauthenticated internet-accessible route by design) and possession of any one validly-signed webhook body — obtainable by the attacker triggering a webhook-eligible action on their own store. No access to `api_secret_key`, tokens, or the victim's credentials is needed, keeping this within the unprivileged-internet-user threat model.

### Recommendation
Include the tenant-identifying header (`shop-domain`) in the signable material that `HmacValidator` verifies for webhooks, or otherwise cryptographically bind `shop` to the body before dispatch, so that `Registry.process` cannot be fed a body/shop pair that Shopify never actually paired together.

### Proof of Concept
1. Attacker owns `attacker.myshopify.com` and registers a webhook handler; they capture a legitimately Shopify-signed webhook request: `raw_body = B`, header `x-shopify-hmac-sha256 = HMAC(secret, B)`, header `x-shopify-shop-domain = attacker.myshopify.com`.
2. Attacker sends a new HTTP request to the same app webhook endpoint with an unmodified `raw_body = B` and unmodified `x-shopify-hmac-sha256`, but with `x-shopify-shop-domain` rewritten to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate(request)` calls `to_signable_string` (`= B`), recomputes the HMAC over `B`, and it matches — validation succeeds [4](#0-3) 
4. `Registry.process` proceeds to call the handler with `WebhookMetadata.new(... shop: request.shop ...)`, where `request.shop` is now `victim.myshopify.com` [5](#0-4) , even though Shopify never generated or signed this event for `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
