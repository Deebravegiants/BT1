Confirmed root cause. The `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read from separate headers that are never included in the HMAC-signed material: [2](#0-1) 

`Registry.process` validates only the HMAC over that signable string, then trusts `request.shop` (and other unauthenticated headers) to build the metadata passed to the app's handler: [3](#0-2) 

### Title
Webhook `shop` (and topic/webhook_id) header not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC computed by `Utils::HmacValidator` binds solely to the body bytes. The `X-Shopify-Shop-Domain` header (exposed via `Request#shop`), along with `topic`, `api-version`, and `webhook-id`, are parsed from headers that fall entirely outside the signed content. `Webhooks::Registry.process` trusts these header-derived fields to route and label the webhook to a specific shop/tenant after HMAC validation succeeds.

### Finding Description
The identity binding that should hold is: `hmac_verified_bytes == bytes_the_app_attributes_to_a_shop`. Here that equality is broken:
- `HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac-sha256` header [4](#0-3) .
- For webhooks, `to_signable_string` is just `@raw_body` [1](#0-0) , so the HMAC never covers the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers.
- `Registry.process` validates HMAC on the body, then immediately reads `request.shop`, `request.topic`, `request.webhook_id`, `request.api_version` from headers and forwards them unauthenticated into `WebhookMetadata`, which the app's handler uses to decide which shop/tenant record to update [3](#0-2) .

Since the app's webhook secret (`api_secret_key`) is shared across all shops installing the app (it is not per-shop), any party capable of causing an HTTP POST with a body/HMAC pair that is valid for *some* topic (e.g., a legitimately-delivered webhook for their own shop, which they fully control and can replay/relay) can pair that valid `(body, hmac)` combination with an arbitrary forged `X-Shopify-Shop-Domain` header. `HmacValidator.validate` will report success because it checks only the body, and the handler will process the payload as belonging to the attacker-chosen shop instead of the shop that actually owns that body content.

### Impact Explanation
This breaks the shop/tenant identity binding for webhook processing (cross-tenant data confusion), matching the "Critical — cross-tenant access" impact category: a handler that persists webhook data keyed by `data.shop` (e.g., updating shop-level settings, marking data deleted, updating billing/app-installation state) can be made to attribute another merchant's legitimate webhook body to a shop chosen by the attacker, or vice versa — attacker-controlled shop content delivered under a victim shop's identity. Any downstream logic that trusts `WebhookMetadata#shop` as authenticated is affected.

### Likelihood Explanation
Exploitability requires the attacker to have access to at least one valid `(body, hmac)` pair signed with the app's shared secret — trivially obtained by any merchant with the app installed on their own store, since Shopify delivers real webhooks (with valid HMACs) to every installed shop using the same app secret. The attacker only needs to relay/replay that request to the app's public webhook endpoint with a modified `shop-domain` header; no access token, API key, or credential theft is required beyond normal use of an installed app instance.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the value that is HMAC-verified, or otherwise cryptographically/authoritatively bind the `shop` header to the signed body — for example, by validating against the session/shop record independently retrieved via an authenticated lookup (e.g. cross-check with `webhook_id`/topic registered per shop via the Admin API) rather than trusting the raw header value once body-HMAC succeeds. At minimum, document and enforce that `request.shop` must not be treated as authenticated identity data by consuming applications, or extend `to_signable_string` to incorporate all Shopify-supplied identifying headers so tampering invalidates the signature.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`; Shopify sends a real webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: HMAC(secret, B)` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker captures this request and resends it to the same endpoint, changing only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`, leaving body `B` and the HMAC header untouched.
3. `Webhooks::Request.new` parses the new `shop` value; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` — still valid, since `to_signable_string` only returns `B`.
4. The handler receives `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: B, ...)` and processes attacker-controlled content `B` as if it originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
