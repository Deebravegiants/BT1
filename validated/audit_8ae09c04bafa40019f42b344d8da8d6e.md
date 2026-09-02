### Title
Webhook `shop-domain` header is trusted for tenant identification but is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw request body when validating a webhook's authenticity, while the `shop` value handed to the application's `WebhookHandler` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never included in the signed payload. This breaks the binding "shop authenticated == shop acted on," allowing an attacker who can obtain one genuine, validly-signed webhook body (e.g. from their own installed/dev shop) to replay it against the app's webhook endpoint while substituting an arbitrary victim shop domain in the header, producing a request that passes `HmacValidator.validate` yet is attributed to a different tenant.

### Finding Description
The webhook signature check computes the HMAC exclusively over `to_signable_string`, which for `Request` returns `@raw_body`: [1](#0-0) 

`HmacValidator.validate` compares the received `hmac` header against `OpenSSL::HMAC.hexdigest` of that signable string, using the app's single, shop-independent `Context.api_secret_key`: [2](#0-1) 

Meanwhile, `Registry.process` trusts `request.shop` — parsed straight from the unauthenticated `shop-domain` header — and forwards it as the tenant identity in `WebhookMetadata` passed to the handler: [3](#0-2) [4](#0-3) [5](#0-4) 

The equality that should hold is:
`shop that authorized/produced the signed bytes == shop the handler is told to act on`

Because the `api_secret_key` is a single app-wide secret (not scoped per shop) and `shop-domain` is excluded from the signable string, this equality does not hold: any correctly-signed `(raw_body, hmac)` pair — obtainable from a legitimately installed shop (including an attacker-controlled dev/trial store) — remains valid under `HmacValidator.validate` no matter what `shop-domain` header value accompanies it. An attacker can therefore submit a request with a genuine `hmac`/`raw_body` pair but an arbitrary victim `shop-domain`, and the gem will report the HMAC as valid and hand the (attacker-controlled) body to the application's handler tagged with the victim's shop, i.e., cross-tenant webhook injection/spoofing.

This is the same bug class as the report's core issue: a value that participates in a security-relevant decision (`shop` used to determine which tenant's data the webhook body affects) is not bound into the cryptographic check that is supposed to authenticate the whole request (the HMAC only binds `raw_body`, not `shop-domain`).

### Impact Explanation
An application relying solely on `ShopifyAPI::Webhooks::Registry.process`/`Request` to validate and dispatch webhooks has no way to know that `data.shop` is unauthenticated. If handler logic uses `data.shop` to select the tenant's stored data/session (a normal and expected pattern, e.g., "look up this shop's `Session`/access token and update local records for topic X"), an attacker can forge webhook deliveries that inject attacker-controlled body content while impersonating an arbitrary victim shop, resulting in cross-tenant data corruption/access — matching the "cross-tenant access" High/Critical impact category.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one validly HMAC-signed webhook body, which is achievable by installing the target app on the attacker's own (free/dev) Shopify store and triggering a webhook event — no privileged credentials, leaked secrets, or social engineering are required. The attacker then only needs to POST that same body/hmac pair to the app's public webhook endpoint with a modified `shopify-shop-domain` header, which any unprivileged internet user with knowledge of the endpoint URL can do.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the signed material, or otherwise cryptographically bind the shop identity to the signature — e.g., validate that the `shop-domain` header matches a shop already known to have installed the app with an active offline session before trusting it, rather than passing the raw header value straight into `WebhookMetadata`. At minimum, document prominently that `data.shop` in `WebhookMetadata` is not authenticated by the HMAC check and must be independently corroborated (e.g., against stored sessions) before being used for tenant-scoped operations.

### Proof of Concept
1. Attacker installs the target app on their own Shopify store (`attacker.myshopify.com`) and triggers a webhook event, capturing the legitimate delivery: `raw_body = B`, header `shopify-hmac-sha256 = H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker sends a forged HTTP request to the app's webhook endpoint with:
   - `raw_body = B` (unchanged)
   - `shopify-hmac-sha256 = H` (unchanged, still valid because `to_signable_string` only returns `raw_body`)
   - `shopify-shop-domain = victim.myshopify.com` (changed)
   - `shopify-topic`, `shopify-webhook-id` set to any values the app expects.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers without validating `shop-domain` against anything, and `Utils::HmacValidator.validate` succeeds because it only recomputes the HMAC over `raw_body`.
4. `Registry.process` dispatches to the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker-controlled parsed body>, ...)`, i.e., the application believes this attacker-crafted body originates from `victim.myshopify.com`. [3](#0-2) [1](#0-0) [6](#0-5)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
